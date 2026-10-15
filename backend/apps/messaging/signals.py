"""Domain event của nhắn tin — điểm mở rộng (thông báo, đẩy qua WebSocket...). Phát sau khi transaction commit."""
from django.dispatch import Signal

message_sent = Signal()  # kwargs: message
