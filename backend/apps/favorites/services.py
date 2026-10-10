"""Thêm / bỏ yêu thích. Thao tác lặp lại không lỗi (bấm hai lần, hai tab cùng lúc)."""
from .models import FavoriteCompany, FavoriteJob


def add_favorite_job(candidate, job) -> bool:
    """Trả về True nếu vừa thêm, False nếu tin đã có trong danh sách yêu thích."""
    # get_or_create tự xử lý trường hợp hai request tạo cùng lúc (vướng ràng buộc unique thì lấy lại bản ghi)
    _, created = FavoriteJob.objects.get_or_create(candidate=candidate, job=job)
    return created


def remove_favorite_job(candidate, job_id) -> None:
    FavoriteJob.objects.filter(candidate=candidate, job_id=job_id).delete()


def add_favorite_company(candidate, company) -> bool:
    _, created = FavoriteCompany.objects.get_or_create(candidate=candidate, company=company)
    return created


def remove_favorite_company(candidate, company_id) -> None:
    FavoriteCompany.objects.filter(candidate=candidate, company_id=company_id).delete()
