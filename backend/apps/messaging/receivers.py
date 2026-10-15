"""Nghe domain event của app connections (đăng ký trong MessagingConfig.ready)."""
import logging

from . import services

logger = logging.getLogger(__name__)


def on_connection_accepted(sender, connection, **kwargs):
    # Chạy sau commit: lỗi ở đây không làm hỏng thao tác chấp nhận lời mời; hội thoại vẫn được
    # tạo lại khi một trong hai bên bấm "Nhắn tin" (POST /conversations/).
    try:
        services.start_conversation_from_connection(connection)
    except Exception:
        logger.exception('Không tạo được hội thoại cho lời mời kết bạn %s', connection.pk)
