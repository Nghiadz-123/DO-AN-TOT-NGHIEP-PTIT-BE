"""Tác vụ nền của CV: bóc tách văn bản sau khi upload.

Hiện chưa có Celery (requirements: giai đoạn AI mới thêm) nên `enqueue_parse` chạy `parse_cv_task`
ngay sau khi transaction commit, trong cùng tiến trình. Khi có Celery chỉ cần:
    @shared_task(autoretry_for=(OSError,), max_retries=3)  # UC-03: thử lại tối đa 3 lần
    def parse_cv_task(cv_id): ...
và trong enqueue_parse gọi `parse_cv_task.delay(str(cv_id))` — service/view không phải sửa.

Frontend luôn coi bóc tách là bất đồng bộ: hiển thị "Đang phân tích" và gọi lại
GET /candidate/cvs/{id}/ khi parse_status là pending/processing.
"""
from django.db import transaction

from .models import CV


def enqueue_parse(cv: CV) -> None:
    cv_id = cv.pk
    # Chạy sau commit: worker (sau này) phải đọc được bản ghi; robust=True để lỗi không làm hỏng request
    transaction.on_commit(lambda: parse_cv_task(cv_id), robust=True)


def parse_cv_task(cv_id) -> None:
    from .services import parse_cv  # import trong hàm: services gọi enqueue_parse của module này

    cv = CV.objects.filter(pk=cv_id).first()
    if cv is None:
        return  # CV đã bị xóa trước khi kịp xử lý
    parse_cv(cv)
