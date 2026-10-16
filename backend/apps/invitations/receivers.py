"""Nghe domain event của app applications (đăng ký trong InvitationsConfig.ready)."""
import logging

from . import services

logger = logging.getLogger(__name__)


def on_application_submitted(sender, application, **kwargs):
    # Chạy sau commit: lỗi ở đây không làm hỏng việc nộp hồ sơ
    try:
        services.mark_applied(application)
    except Exception:
        logger.exception('Không cập nhật được thư mời cho hồ sơ %s', application.pk)
