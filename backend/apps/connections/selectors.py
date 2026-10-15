"""Các truy vấn đọc lời mời kết bạn / danh sách bạn bè."""
from django.db.models import Q

from .models import Connection, ConnectionStatus

# Thông tin hiển thị của hai bên (hồ sơ ứng viên / nhà tuyển dụng + công ty) lấy cùng một query
PARTICIPANT_RELATED = (
    'requester__candidate_profile', 'requester__recruiter__company',
    'addressee__candidate_profile', 'addressee__recruiter__company',
)


def _involving(user) -> Q:
    return Q(requester=user) | Q(addressee=user)


def pair_q(user_a, user_b) -> Q:
    return Q(requester=user_a, addressee=user_b) | Q(requester=user_b, addressee=user_a)


def user_connections(user):
    """Mọi lời mời / quan hệ có `user` tham gia (dùng cho các thao tác trên một bản ghi)."""
    return Connection.objects.filter(_involving(user)).select_related(*PARTICIPANT_RELATED, 'job')


def friends(user, search: str = ''):
    """Bạn bè (đã chấp nhận lời mời), kết bạn gần nhất trước. `search`: tìm theo tên người còn lại."""
    qs = user_connections(user).filter(status=ConnectionStatus.ACCEPTED)
    if search:
        qs = qs.filter(
            Q(requester=user, addressee__full_name__icontains=search)
            | Q(addressee=user, requester__full_name__icontains=search)
        )
    return qs.order_by('-responded_at', '-created_at')


def received_requests(user):
    """Lời mời đang chờ `user` phản hồi."""
    return user_connections(user).filter(addressee=user, status=ConnectionStatus.PENDING)


def sent_requests(user):
    """Lời mời `user` đã gửi chưa thành bạn bè (đang chờ hoặc bị từ chối)."""
    return user_connections(user).filter(requester=user).exclude(status=ConnectionStatus.ACCEPTED)


def connection_between(user_a, user_b) -> Connection | None:
    return Connection.objects.filter(pair_q(user_a, user_b)).first()


def are_connected(user_a, user_b) -> bool:
    return Connection.objects.filter(pair_q(user_a, user_b), status=ConnectionStatus.ACCEPTED).exists()


def friend_ids(user) -> set:
    """Id tài khoản bạn bè của `user`."""
    pairs = Connection.objects.filter(_involving(user), status=ConnectionStatus.ACCEPTED).values_list(
        'requester_id', 'addressee_id'
    )
    return {addressee if requester == user.pk else requester for requester, addressee in pairs}


def connection_map(user, other_user_ids) -> dict:
    """{id tài khoản khác: Connection} giữa `user` và từng tài khoản trong danh sách."""
    other_user_ids = list(other_user_ids)
    if not other_user_ids:
        return {}
    qs = Connection.objects.filter(
        Q(requester=user, addressee_id__in=other_user_ids) | Q(addressee=user, requester_id__in=other_user_ids)
    )
    return {c.addressee_id if c.requester_id == user.pk else c.requester_id: c for c in qs}
