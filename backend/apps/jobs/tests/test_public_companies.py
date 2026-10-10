from datetime import timedelta

import pytest
from django.utils import timezone

from apps.catalog.models import Industry, Location
from apps.employers import services as employer_services
from apps.jobs import services
from apps.jobs.models import Job

pytestmark = pytest.mark.django_db

COMPANIES = '/api/v1/companies/'


def test_directory_lists_alive_companies_with_open_job_count(api_client, recruiter, other_recruiter, make_job,
                                                             make_employer):
    make_job(title='Đang tuyển')
    make_job(title='Bản nháp', publish=False)
    closed = make_job(title='Đã đóng')
    services.close_job(closed, by=None)
    expired = make_job(title='Hết hạn')
    Job.objects.filter(pk=expired.pk).update(deadline=timezone.localdate() - timedelta(days=1))
    make_job(title='Đã xóa').soft_delete()
    make_employer(company_name='Công ty đã xóa').company.soft_delete()

    res = api_client.get(COMPANIES)

    assert res.status_code == 200
    # Chỉ đếm tin đang tuyển; công ty có nhiều tin đang tuyển đứng trước
    assert [(c['name'], c['open_job_count']) for c in res.data['results']] == [('ACME', 1), ('Other Corp', 0)]
    assert {'logo_url', 'location', 'industry', 'company_size', 'verification_status'} <= res.data['results'][0].keys()


def test_directory_search_and_filters(api_client, recruiter, other_recruiter):
    health = Industry.objects.get(slug='y-te-duoc-pham')
    da_nang = Location.objects.get(slug='da-nang')
    employer_services.update_company(other_recruiter.company, data={'industry': health, 'location': da_nang})

    def names(params):
        return [c['name'] for c in api_client.get(COMPANIES, params).data['results']]

    assert names({'q': 'acm'}) == ['ACME']
    assert names({'industry': health.id}) == ['Other Corp']
    assert names({'location': da_nang.id}) == ['Other Corp']


def test_company_profile_and_its_open_jobs(api_client, recruiter, other_recruiter, make_job):
    make_job(title='Kế toán tổng hợp')
    make_job(company=other_recruiter.company, created_by=other_recruiter.user, title='Nhân viên lễ tân')

    res = api_client.get(f'{COMPANIES}{recruiter.company.id}/')

    assert res.status_code == 200
    assert res.data['open_job_count'] == 1
    assert {'website', 'address', 'founded_year', 'description'} <= res.data.keys()
    assert 'tax_code' not in res.data and 'email' not in res.data
    jobs = api_client.get('/api/v1/jobs/', {'company': recruiter.company.id}).data['results']
    assert [j['title'] for j in jobs] == ['Kế toán tổng hợp']


def test_deleted_company_profile_is_hidden(api_client, other_recruiter):
    other_recruiter.company.soft_delete()

    assert api_client.get(f'{COMPANIES}{other_recruiter.company.id}/').status_code == 404
