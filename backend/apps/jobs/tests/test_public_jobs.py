from datetime import timedelta

import pytest
from django.utils import timezone

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
    make_job(title='React Developer', skills=('React',), level='junior', job_type='full_time')
    make_job(title='Data Analyst', skills=('SQL', 'Power BI'), level='middle', job_type='part_time', location_id=2)

    def titles(params):
        return [j['title'] for j in api_client.get(PUBLIC, params).data['results']]

    assert titles({'q': 'power bi'}) == ['Data Analyst']  # tìm theo kỹ năng
    assert titles({'q': 'acme'}) == ['Data Analyst', 'React Developer']  # tìm theo tên công ty
    assert titles({'level': 'junior'}) == ['React Developer']
    assert titles({'job_type': 'part_time'}) == ['Data Analyst']
    assert titles({'location': 2}) == ['Data Analyst']


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
