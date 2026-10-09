"""Domain event của CV — điểm mở rộng cho module AI (giai đoạn sau).

cvs không biết ai lắng nghe. Ví dụ ở giai đoạn AI, apps/ai đăng ký receiver trong AppConfig.ready():
    cv_parsed  -> phân tích, chấm điểm CV (cv_analyses), sinh embedding và index vào ChromaDB,
                  tính lại gợi ý việc làm cho ứng viên
    cv_deleted -> gỡ CV khỏi vector store
Mọi event được phát sau khi transaction commit (common.utils.send_on_commit).
"""
from django.dispatch import Signal

cv_uploaded = Signal()  # kwargs: cv
cv_parsed = Signal()    # kwargs: cv (parse_status=completed, đã có raw_text, parsed_data)
cv_deleted = Signal()   # kwargs: cv
