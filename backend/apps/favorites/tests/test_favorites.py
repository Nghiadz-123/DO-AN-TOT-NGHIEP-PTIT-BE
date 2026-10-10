import pytest

from apps.favorites.models import FavoriteCompany, FavoriteJob
from apps.jobs import services as job_services

pytestmark = pytest.mark.django_db

JOBS = '/api/v1/candidate/favorites/jobs/'
COMPANIES = '/api/v1/candidate/favorites/companies/'
IDS = '/api/v1/candidate/favorites/ids/'


def test_add_list_and_remove_favorite_job(candidate_client, make_job):
    job = make_job(title='Kế toán tổng hợp')

    res = candidate_client.post(JOBS, {'job_id': str(job.id)}, format='json')

    assert res.status_code == 201, res.data
    assert res.data['title'] == 'Kế toán tổng hợp'
    assert res.data['favorited_at']
    # Thêm lần nữa: không tạo trùng
    assert candidate_client.post(JOBS, {'job_id': str(job.id)}, format='json').status_code == 200
    assert FavoriteJob.objects.count() == 1
    listed = candidate_client.get(JOBS).data
    assert [j['id'] for j in listed['results']] == [str(job.id)]
    assert candidate_client.get(IDS).data == {'jobs': [str(job.id)], 'companies': []}

    assert candidate_client.delete(f'{JOBS}{job.id}/').status_code == 204
    assert candidate_client.get(JOBS).data['count'] == 0
    assert candidate_client.delete(f'{JOBS}{job.id}/').status_code == 204  # bỏ lần nữa cũng không lỗi


def test_draft_or_unknown_job_cannot_be_favorited(candidate_client, make_job, recruiter):
    draft = make_job(publish=False)

    res = candidate_client.post(JOBS, {'job_id': str(draft.id)}, format='json')

    assert res.status_code == 400
    assert res.data['errors']['job_id'] == ['Tin tuyển dụng không tồn tại.']
    assert candidate_client.post(JOBS, {'job_id': str(recruiter.company.id)}, format='json').status_code == 400


def test_closed_job_stays_deleted_job_disappears(candidate_client, make_job):
    closed = make_job(title='Đã đóng')
    deleted = make_job(title='Đã xóa')
    for job in (closed, deleted):
        candidate_client.post(JOBS, {'job_id': str(job.id)}, format='json')
    job_services.close_job(closed, by=None)
    deleted.soft_delete()

    results = candidate_client.get(JOBS).data['results']

    assert [(j['title'], j['status']) for j in results] == [('Đã đóng', 'closed')]
    assert candidate_client.get(IDS).data['jobs'] == [str(closed.id)]


def test_favorite_companies(candidate_client, recruiter, other_recruiter, make_job):
    make_job()  # ACME có 1 tin đang tuyển

    res = candidate_client.post(COMPANIES, {'company_id': str(recruiter.company.id)}, format='json')

    assert res.status_code == 201, res.data
    assert (res.data['name'], res.data['open_job_count']) == ('ACME', 1)
    candidate_client.post(COMPANIES, {'company_id': str(other_recruiter.company.id)}, format='json')
    other_recruiter.company.soft_delete()  # công ty đã xóa không còn hiển thị
    assert [c['name'] for c in candidate_client.get(COMPANIES).data['results']] == ['ACME']
    assert candidate_client.get(IDS).data['companies'] == [str(recruiter.company.id)]

    assert candidate_client.delete(f'{COMPANIES}{recruiter.company.id}/').status_code == 204
    assert candidate_client.get(COMPANIES).data['count'] == 0


def test_favorites_are_private(candidate_client, candidate, make_job, make_candidate, recruiter):
    job = make_job()
    other, _ = make_candidate()
    FavoriteJob.objects.create(candidate=other, job=job)
    FavoriteCompany.objects.create(candidate=other, company=recruiter.company)

    assert candidate_client.get(JOBS).data['count'] == 0
    assert candidate_client.get(IDS).data == {'jobs': [], 'companies': []}
    # Bỏ yêu thích theo id tin / công ty chỉ ảnh hưởng ứng viên đang đăng nhập
    candidate_client.delete(f'{JOBS}{job.id}/')
    candidate_client.delete(f'{COMPANIES}{recruiter.company.id}/')
    assert FavoriteJob.objects.filter(candidate=other).exists()
    assert FavoriteCompany.objects.filter(candidate=other).exists()


def test_only_candidates_have_favorites(api_client, employer_client):
    assert api_client.get(JOBS).status_code == 401
    assert employer_client.get(JOBS).status_code == 403
    assert employer_client.get(IDS).status_code == 403
