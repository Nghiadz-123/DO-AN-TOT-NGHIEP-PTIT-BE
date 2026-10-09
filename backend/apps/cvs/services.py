"""Nghiệp vụ CV của ứng viên (các thao tác ghi). View chỉ validate input rồi gọi vào đây."""
import logging
import re
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.candidates.models import CandidateProfile
from common.exceptions import BusinessError
from common.utils import file_sha256, send_on_commit

from . import parsers, signals
from .models import CV, CVParseStatus
from .tasks import enqueue_parse

logger = logging.getLogger(__name__)

TITLE_MAX_LENGTH = 150
FILENAME_MAX_LENGTH = 255
REPARSABLE_STATUSES = (CVParseStatus.PENDING, CVParseStatus.FAILED)
FILE_MISSING_MESSAGE = 'Không tìm thấy file CV. Vui lòng tải lên lại.'
UNEXPECTED_ERROR_MESSAGE = 'Đã có lỗi khi đọc CV. Vui lòng thử lại sau hoặc tải lên file khác.'

_WHITESPACE = re.compile(r'\s+')


@transaction.atomic
def upload_cv(
    *, candidate, file, mime_type: str, title: str = '', is_default: bool = False, language: str = ''
) -> CV:
    """Lưu CV mới (file đã qua validators.validate_cv_file) rồi xếp lịch bóc tách văn bản.

    CV đầu tiên của ứng viên tự động là CV mặc định. File trùng nội dung (SHA-256) với một CV
    đang có bị từ chối để danh sách không lặp và kết quả AI dùng lại được theo file_hash.
    """
    _lock_candidate(candidate.pk)
    if CV.objects.filter(candidate=candidate).count() >= settings.CANDIDATE_MAX_CVS:
        raise BusinessError(
            f'Bạn chỉ được lưu tối đa {settings.CANDIDATE_MAX_CVS} CV. Hãy xóa bớt CV cũ trước khi tải lên.',
            code='cv_limit_reached',
        )
    file_hash = file_sha256(file)
    duplicate = CV.objects.filter(candidate=candidate, file_hash=file_hash).first()
    if duplicate is not None:
        raise BusinessError(
            f'CV này đã được tải lên trước đó với tên "{duplicate.title}".', code='duplicate_cv', status_code=409
        )

    current_default = CV.objects.filter(candidate=candidate, is_default=True)
    make_default = is_default or not current_default.exists()
    if make_default:
        current_default.update(is_default=False, updated_at=timezone.now())

    original_filename = _clean_filename(file.name)
    cv = CV(
        candidate=candidate,
        title=_clean_title(title) or _title_from_filename(original_filename),
        original_filename=original_filename,
        mime_type=mime_type,
        file_size=file.size,
        file_hash=file_hash,
        language=language,
        is_default=make_default,
    )
    cv.file.save(original_filename, file, save=False)
    try:
        cv.save()
    except Exception:
        cv.file.delete(save=False)  # không để lại file mồ côi khi ghi DB lỗi
        raise
    enqueue_parse(cv)
    send_on_commit(signals.cv_uploaded, sender=CV, cv=cv)
    return cv


def update_cv(cv: CV, *, title: str) -> CV:
    cv.title = _clean_title(title)
    cv.save(update_fields=['title', 'updated_at'])
    return cv


@transaction.atomic
def set_default_cv(cv: CV) -> CV:
    _lock_candidate(cv.candidate_id)
    cv.refresh_from_db(fields=['is_default'])
    if not cv.is_default:
        # Bỏ CV mặc định cũ trước để không vi phạm uq_cvs_default
        CV.objects.filter(candidate_id=cv.candidate_id, is_default=True).update(
            is_default=False, updated_at=timezone.now()
        )
        cv.is_default = True
        cv.save(update_fields=['is_default', 'updated_at'])
    return cv


@transaction.atomic
def delete_cv(cv: CV) -> None:
    """Xóa mềm CV.

    - CV đã dùng để ứng tuyển: giữ file vì nhà tuyển dụng vẫn cần xem hồ sơ đã nhận.
    - CV chưa dùng: xóa luôn file (dữ liệu cá nhân, không giữ khi không còn cần).
    Xóa CV mặc định thì CV mới nhất còn lại trở thành mặc định.
    """
    _lock_candidate(cv.candidate_id)
    was_default = cv.is_default
    cv.is_default = False
    cv.deleted_at = timezone.now()
    fields = ['is_default', 'deleted_at', 'updated_at']
    if cv.file and not cv.applications.exists():
        storage, name = cv.file.storage, cv.file.name
        transaction.on_commit(lambda: storage.delete(name))  # chỉ xóa file khi DB đã commit
        cv.file = ''
        fields.append('file')
    cv.save(update_fields=fields)

    if was_default:
        successor = CV.objects.filter(candidate_id=cv.candidate_id).order_by('-created_at').first()
        if successor is not None:
            successor.is_default = True
            successor.save(update_fields=['is_default', 'updated_at'])
    send_on_commit(signals.cv_deleted, sender=CV, cv=cv)


@transaction.atomic
def reparse_cv(cv: CV) -> CV:
    """Bóc tách lại CV bị lỗi (hoặc kẹt ở hàng đợi)."""
    if cv.parse_status not in REPARSABLE_STATUSES:
        current = CVParseStatus(cv.parse_status).label
        raise BusinessError(
            f'Không thể bóc tách lại CV đang ở trạng thái "{current}".',
            code='invalid_parse_status',
            status_code=409,
        )
    cv.parse_status = CVParseStatus.PENDING
    cv.parse_error = ''
    cv.save(update_fields=['parse_status', 'parse_error', 'updated_at'])
    enqueue_parse(cv)
    return cv


def parse_cv(cv: CV) -> CV:
    """Bóc tách văn bản + thông tin cơ bản của CV (không dùng AI), gọi từ tasks.parse_cv_task.

    Không ném lỗi ra ngoài: thất bại thì parse_status=failed kèm thông điệp cho ứng viên.
    Thành công thì phát cv_parsed để module AI phân tích tiếp.
    """
    cv.parse_status = CVParseStatus.PROCESSING
    cv.parse_error = ''
    cv.save(update_fields=['parse_status', 'parse_error', 'updated_at'])
    if not cv.file:
        return _mark_parse_failed(cv, FILE_MISSING_MESSAGE)
    try:
        with cv.file.open('rb') as fh:
            extracted = parsers.extract_text(fh, cv.mime_type)
    except parsers.CVParseError as exc:
        return _mark_parse_failed(cv, str(exc))
    except FileNotFoundError:
        return _mark_parse_failed(cv, FILE_MISSING_MESSAGE)
    except Exception:
        logger.exception('Bóc tách CV %s thất bại', cv.pk)
        return _mark_parse_failed(cv, UNEXPECTED_ERROR_MESSAGE)

    cv.raw_text = extracted.text
    cv.parsed_data = parsers.build_parsed_data(extracted)
    cv.language = cv.language or parsers.detect_language(extracted.text)
    cv.parse_status = CVParseStatus.COMPLETED
    cv.parsed_at = timezone.now()
    cv.save(update_fields=['raw_text', 'parsed_data', 'language', 'parse_status', 'parsed_at', 'updated_at'])
    send_on_commit(signals.cv_parsed, sender=CV, cv=cv)
    return cv


def _mark_parse_failed(cv: CV, message: str) -> CV:
    cv.parse_status = CVParseStatus.FAILED
    cv.parse_error = message
    cv.raw_text = ''
    cv.parsed_data = None
    cv.parsed_at = None
    cv.save(update_fields=['parse_status', 'parse_error', 'raw_text', 'parsed_data', 'parsed_at', 'updated_at'])
    return cv


def _lock_candidate(candidate_id) -> None:
    """Khóa hồ sơ ứng viên trong transaction để các thao tác CV đồng thời của cùng một ứng viên chạy
    tuần tự (giới hạn số CV, ràng buộc tối đa 1 CV mặc định). SQLite bỏ qua select_for_update."""
    list(CandidateProfile.objects.select_for_update().filter(pk=candidate_id).values_list('pk', flat=True))


def _clean_title(title: str) -> str:
    return _WHITESPACE.sub(' ', title or '').strip()[:TITLE_MAX_LENGTH]


def _title_from_filename(filename: str) -> str:
    return _clean_title(Path(filename).stem.replace('_', ' ')) or 'CV'


def _clean_filename(name: str) -> str:
    name = ''.join(ch for ch in Path(name or '').name if ch.isprintable()).strip() or 'cv'
    if len(name) > FILENAME_MAX_LENGTH:
        suffix = Path(name).suffix
        name = name[: FILENAME_MAX_LENGTH - len(suffix)] + suffix
    return name
