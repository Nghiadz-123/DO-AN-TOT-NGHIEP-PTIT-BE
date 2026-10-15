"""Nghiệp vụ kết bạn: gửi / chấp nhận / từ chối lời mời, hủy lời mời, hủy kết bạn.

Quy tắc:
- Chỉ nhà tuyển dụng (recruiter đang hoạt động) gửi lời mời, và chỉ tới ứng viên mà công ty của họ được
  tìm thấy (candidates.selectors.discoverable_candidates: hồ sơ công khai hoặc đã ứng tuyển vào công ty).
- Mỗi cặp tài khoản một lời mời; bị từ chối thì sau RESEND_COOLDOWN mới được mời lại.
- Người nhận chấp nhận / từ chối; người gửi hủy được lời mời đang chờ; bạn bè thì một trong hai bên hủy kết bạn.
"""
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.candidates import selectors as candidate_selectors
from common.exceptions import BusinessError
from common.utils import send_on_commit

from . import signals
from .models import Connection, ConnectionStatus
from .selectors import pair_q

RESEND_COOLDOWN = timedelta(days=7)
MESSAGE_MAX_LENGTH = 500


@transaction.atomic
def send_request(*, recruiter, addressee, message: str = '', job=None) -> Connection:
    """Nhà tuyển dụng gửi lời mời kết bạn tới tài khoản ứng viên (`job`: tin liên quan, cùng công ty)."""
    if (
        addressee.role != UserRole.CANDIDATE
        or not candidate_selectors.discoverable_candidates(recruiter.company).filter(user=addressee).exists()
    ):
        # Không phân biệt "không tồn tại" và "không được phép thấy" để không lộ hồ sơ riêng tư
        raise BusinessError('Không tìm thấy ứng viên.', code='candidate_not_found', status_code=404)
    if job is not None and job.company_id != recruiter.company_id:
        raise BusinessError('Tin tuyển dụng không tồn tại.', code='job_not_found', status_code=404)

    user = recruiter.user
    message = message.strip()[:MESSAGE_MAX_LENGTH]
    connection = Connection.objects.select_for_update().filter(pair_q(user, addressee)).first()
    if connection is None:
        try:
            with transaction.atomic():
                connection = Connection.objects.create(requester=user, addressee=addressee, message=message, job=job)
        except IntegrityError as exc:  # hai request gửi cùng lúc
            raise BusinessError(
                'Bạn đã gửi lời mời cho ứng viên này.', code='request_pending', status_code=409
            ) from exc
    else:
        _ensure_can_resend(connection)
        connection.requester, connection.addressee = user, addressee
        connection.status = ConnectionStatus.PENDING
        connection.message, connection.job = message, job
        connection.created_at, connection.responded_at = timezone.now(), None
        connection.save()
    send_on_commit(signals.connection_requested, sender=Connection, connection=connection)
    return connection


def _ensure_can_resend(connection: Connection) -> None:
    if connection.status == ConnectionStatus.ACCEPTED:
        raise BusinessError('Hai bạn đã là bạn bè.', code='already_connected', status_code=409)
    if connection.status == ConnectionStatus.PENDING:
        raise BusinessError(
            'Đã có lời mời kết bạn giữa hai tài khoản, đang chờ phản hồi.', code='request_pending', status_code=409
        )
    resend_at = connection.responded_at + RESEND_COOLDOWN
    if timezone.now() < resend_at:
        raise BusinessError(
            f'Ứng viên đã từ chối lời mời. Bạn có thể gửi lại từ ngày {timezone.localtime(resend_at):%d/%m/%Y}.',
            code='request_declined_recently',
            status_code=409,
        )


@transaction.atomic
def accept_request(connection: Connection, *, by) -> Connection:
    connection = _lock_pending_for_addressee(connection, by)
    connection.status = ConnectionStatus.ACCEPTED
    connection.responded_at = timezone.now()
    connection.save(update_fields=['status', 'responded_at', 'updated_at'])
    send_on_commit(signals.connection_accepted, sender=Connection, connection=connection)
    return connection


@transaction.atomic
def decline_request(connection: Connection, *, by) -> Connection:
    connection = _lock_pending_for_addressee(connection, by)
    connection.status = ConnectionStatus.DECLINED
    connection.responded_at = timezone.now()
    connection.save(update_fields=['status', 'responded_at', 'updated_at'])
    return connection


@transaction.atomic
def remove_connection(connection: Connection, *, by) -> None:
    """Hủy kết bạn (một trong hai bên) hoặc hủy lời mời đang chờ (người gửi).

    Lời mời đã bị từ chối được giữ lại để tính thời gian chờ gửi lại (RESEND_COOLDOWN).
    Hội thoại cũ vẫn xem được nhưng không gửi thêm tin nhắn (messaging kiểm tra are_connected).
    """
    connection = Connection.objects.select_for_update().get(pk=connection.pk)
    if connection.status == ConnectionStatus.ACCEPTED:
        allowed = by.pk in (connection.requester_id, connection.addressee_id)
    else:
        allowed = connection.status == ConnectionStatus.PENDING and by.pk == connection.requester_id
    if not allowed:
        message = (
            'Hãy dùng chức năng từ chối lời mời.' if connection.status == ConnectionStatus.PENDING
            else 'Không thể xóa lời mời đã bị từ chối.'
        )
        raise BusinessError(message, code='invalid_connection_action', status_code=409)
    connection.delete()


def _lock_pending_for_addressee(connection: Connection, user) -> Connection:
    connection = Connection.objects.select_for_update().get(pk=connection.pk)
    if connection.addressee_id != user.pk:
        raise BusinessError('Chỉ người nhận được phản hồi lời mời.', code='invalid_connection_action', status_code=403)
    if connection.status != ConnectionStatus.PENDING:
        raise BusinessError(
            f'Lời mời đang ở trạng thái "{ConnectionStatus(connection.status).label}".',
            code='invalid_connection_action',
            status_code=409,
        )
    return connection
