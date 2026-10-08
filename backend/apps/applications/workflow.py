"""Pipeline ATS (state machine) cho hồ sơ ứng tuyển.

    applied ──▶ screening ──▶ interview ──▶ offer ──▶ hired
       │            │             │           │
       └────────────┴─────────────┴───────────┴──▶ rejected ──(mở lại)──▶ screening
    applied ──────────────────▶ interview   (mời phỏng vấn ngay, bỏ qua sàng lọc)

`withdrawn` do ứng viên tự rút (API ứng viên - giai đoạn sau); `hired`, `withdrawn` là trạng thái cuối.
"""
from .models import ApplicationStatus as S

TRANSITIONS: dict[str, tuple[str, ...]] = {
    S.APPLIED: (S.SCREENING, S.INTERVIEW, S.REJECTED),
    S.SCREENING: (S.INTERVIEW, S.REJECTED),
    S.INTERVIEW: (S.OFFER, S.REJECTED),
    S.OFFER: (S.HIRED, S.REJECTED),
    S.REJECTED: (S.SCREENING,),
    S.HIRED: (),
    S.WITHDRAWN: (),
}

# Trạng thái nhà tuyển dụng được phép chuyển tới
EMPLOYER_TARGET_STATUSES = (S.SCREENING, S.INTERVIEW, S.OFFER, S.HIRED, S.REJECTED)

# Hồ sơ đang trong quy trình tuyển (chưa có kết quả)
IN_PROGRESS_STATUSES = (S.SCREENING, S.INTERVIEW, S.OFFER)


def allowed_transitions(status: str) -> list[str]:
    return list(TRANSITIONS.get(status, ()))


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in TRANSITIONS.get(from_status, ())
