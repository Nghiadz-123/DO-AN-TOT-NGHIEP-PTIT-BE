from datetime import timedelta

import pytest
from django.utils import timezone

from apps.catalog.models import Industry
from apps.jobs import services
from apps.jobs.models import Job

pytestmark = pytest.mark.django_db

PUBLIC = '/api/v1/jobs/'


def test_public_list_shows_only_open_jobs(api_client, make_job, other_recruiter):
    open_job = make_job(title='Đang tuyển')
    make_job(title='Bản nháp', publish=False)
    closed = make_job(title='Đã đóng')
    services.close_job(closed, by=None)
    expired = make_job(title='Hết hạn')
    Job.objects.filter(pk=expired.pk).update(deadline=timezone.localdate() - timedelta(days=1))
    deleted = make_job(title='Đã xóa')
    deleted.soft_delete()
    other_company_job = make_job(company=other_recruiter.company, created_by=other_recruiter.user, title='Công ty xóa')
    other_recruiter.company.soft_delete()

    res = api_client.get(PUBLIC)

    assert res.status_code == 200
    assert [j['id'] for j in res.data['results']] == [str(open_job.id)]
    assert other_company_job.id != open_job.id


def test_public_filters(api_client, make_job):
    accounting = Industry.objects.get(slug='ke-toan-kiem-toan')
    make_job(title='Lập trình viên React', skills=('React',), level='staff', job_type='full_time')
    make_job(
        title='Kế toán trưởng', skills=('MISA', 'Excel'), level='manager', job_type='part_time', location_id=2,
        industry=accounting,
    )

    def titles(params):
        return [j['title'] for j in api_client.get(PUBLIC, params).data['results']]

    assert titles({'q': 'misa'}) == ['Kế toán trưởng']  # tìm theo kỹ năng
    assert titles({'q': 'acme'}) == ['Kế toán trưởng', 'Lập trình viên React']  # tìm theo tên công ty
    assert titles({'q': 'kiểm toán'}) == ['Kế toán trưởng']  # tìm theo tên ngành nghề
    assert titles({'level': 'staff'}) == ['Lập trình viên React']
    assert titles({'job_type': 'part_time'}) == ['Kế toán trưởng']
    assert titles({'location': 2}) == ['Kế toán trưởng']
    assert titles({'industry': accounting.id}) == ['Kế toán trưởng']


def test_public_filter_by_posted_time(api_client, make_job):
    make_job(title='Mới đăng')
    old = make_job(title='Đăng 10 ngày trước')
    Job.objects.filter(pk=old.pk).update(published_at=timezone.now() - timedelta(days=10))

    def titles(params):
        return [j['title'] for j in api_client.get(PUBLIC, params).data['results']]

    assert titles({'posted_within': '1'}) == ['Mới đăng']
    assert titles({'posted_within': '14'}) == ['Mới đăng', 'Đăng 10 ngày trước']
    assert api_client.get(PUBLIC, {'posted_within': '2'}).status_code == 400  # chỉ nhận các mốc có sẵn


def test_public_list_includes_industry(api_client, make_job):
    make_job(industry=Industry.objects.get(slug='y-te-duoc-pham'))

    job = api_client.get(PUBLIC).data['results'][0]

    assert job['industry']['name'] == 'Y tế - Dược phẩm'


def test_public_detail_hides_drafts_and_counts_views(api_client, make_job):
    draft = make_job(publish=False)
    job = make_job()

    assert api_client.get(f'{PUBLIC}{draft.id}/').status_code == 404
    res = api_client.get(f'{PUBLIC}{job.id}/')
    assert res.status_code == 200
    assert res.data['company']['name'] == 'ACME'
    assert {'description', 'requirements', 'benefits', 'application_count'} <= res.data.keys()
    api_client.get(f'{PUBLIC}{job.id}/')
    job.refresh_from_db()
    assert job.view_count == 2


def test_closed_job_detail_is_still_visible(api_client, make_job):
    job = make_job()
    services.close_job(job, by=None)

    res = api_client.get(f'{PUBLIC}{job.id}/')

    assert res.status_code == 200
    assert res.data['status'] == 'closed'


def test_public_api_ignores_stale_token(api_client, make_job):
    make_job()
    api_client.credentials(HTTP_AUTHORIZATION='Bearer token-het-han')

    assert api_client.get(PUBLIC).status_code == 200
    assert api_client.get('/api/v1/catalog/locations/').status_code == 200
