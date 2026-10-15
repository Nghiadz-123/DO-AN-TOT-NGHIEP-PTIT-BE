"""Domain event của kết bạn. Phát sau khi transaction commit (common.utils.send_on_commit).

    connection_requested -> (sau này) thông báo cho ứng viên có lời mời mới
    connection_accepted  -> messaging tạo hội thoại, chuyển lời nhắn kèm lời mời thành tin nhắn đầu tiên
"""
from django.dispatch import Signal

connection_requested = Signal()  # kwargs: connection
connection_accepted = Signal()   # kwargs: connection
