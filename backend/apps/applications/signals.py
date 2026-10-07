"""Domain event của hồ sơ ứng tuyển — điểm mở rộng cho module AI (giai đoạn sau), ví dụ:
    application_submitted      -> chấm điểm độ khớp CV - JD (match_results), chạy nền bằng Celery
    application_status_changed -> thông báo cho ứng viên, thống kê thời gian tuyển
Phát sau khi transaction commit.
"""
from django.dispatch import Signal

application_submitted = Signal()       # kwargs: application
application_status_changed = Signal()  # kwargs: application, from_status, to_status, changed_by
