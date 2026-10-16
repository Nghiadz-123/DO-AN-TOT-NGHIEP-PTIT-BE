"""Nghe domain event của app cvs và jobs (đăng ký trong AiConfig.ready)."""
import logging

from apps.jobs import selectors as job_selectors

from .llm.exceptions import AINotConfiguredError
from .services import cv_analysis
from .vectorstore import indexer

logger = logging.getLogger(__name__)


def on_cv_deleted(sender, cv, **kwargs):
    # Chạy sau commit: lỗi ở đây không làm hỏng thao tác xóa CV của ứng viên
    try:
        cv_analysis.delete_cv_data(cv)
    except Exception:
        logger.exception('Không xóa được dữ liệu AI của CV %s', cv.pk)


def on_job_changed(sender, job, **kwargs):
    """Tin được đăng / sửa: embedding ngay để ứng viên đầu tiên dùng gợi ý việc làm không phải chờ.

    Chỉ embedding tin đang tuyển (gợi ý chỉ dùng các tin này). Tin sửa mà nội dung embedding không đổi thì không gọi
    API (indexer so mã băm). Chạy sau commit nên lỗi (Gemini quá tải, hết quota, chưa có key) không làm hỏng việc đăng
    tin: chỉ ghi log, tin sẽ được embedding bù ở lần ứng viên gọi gợi ý đầu tiên.
    """
    try:
        indexer.sync_jobs(job_selectors.public_jobs().filter(pk=job.pk))
    except AINotConfiguredError:
        logger.info('Chưa cấu hình AI nên chưa embedding tin %s', job.pk)
    except Exception:
        logger.warning('Không embedding được tin %s, sẽ thử lại khi có ứng viên dùng gợi ý', job.pk, exc_info=True)
