"""Domain event của tin tuyển dụng — điểm mở rộng cho các module sau (vd. AI).

jobs không biết ai lắng nghe. Ví dụ ở giai đoạn AI, apps/ai đăng ký receiver trong AppConfig.ready():
    job_published  -> sinh embedding JD, index vào ChromaDB
    job_updated    -> index lại JD, đánh dấu match_results cần chấm lại
    job_unpublished / job_deleted -> gỡ JD khỏi vector store
Mọi event được phát sau khi transaction commit (common.utils.send_on_commit).
"""
from django.dispatch import Signal

job_published = Signal()    # kwargs: job
job_updated = Signal()      # kwargs: job, changed_fields
job_unpublished = Signal()  # kwargs: job (status: paused/closed)
job_deleted = Signal()      # kwargs: job
