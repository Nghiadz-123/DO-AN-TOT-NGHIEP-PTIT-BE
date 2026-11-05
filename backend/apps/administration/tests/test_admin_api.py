"""API trang quản trị hệ thống (/api/v1/admin/...): chỉ admin (role admin hoặc is_staff) dùng được."""
import pytest

from apps.accounts.models import User, UserRole
from apps.employers.models import Company, VerificationStatus
from apps.jobs.models import Job, JobStatus
from conftest import PASSWORD, client_for

pytestmark = pytest.mark.django_db

ADMIN = '/api/v1/admin'
MISSING_ID = '00000000-0000-0000-0000-000000000000'
USER_FIELDS = {'id', 'email', 'full_name', 'phone', 'role', 'is_active', 'is_staff', 'created_at'}


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser('admin@test.com', PASSWORD, full_name='Quản trị viên')


@pytest.fixture
def admin_client(admin_user):
    return client_for(admin_user)


# ------------------------------------------------------------------------------------------ quyền truy cập
def test_requires_system_admin(api_client, candidate_client, employer_client):
    assert api_client.get(f'{ADMIN}/overview/').status_code == 401
    assert candidate_client.get(f'{ADMIN}/overview/').status_code == 403
    assert employer_client.get(f'{ADMIN}/users/').status_code == 403
    assert employer_client.patch(f'{ADMIN}/jobs/{MISSING_ID}/', {'status': 'closed'}, format='json').status_code == 403


def test_staff_user_is_system_admin(recruiter):
    recruiter.user.is_staff = True
    recruiter.user.save()

    assert client_for(recruiter.user).get(f'{ADMIN}/overview/').status_code == 200


# ------------------------------------------------------------------------------------------ tổng quan
def test_overview_counts_and_recent_items(admin_client, admin_user, recruiter, candidate, make_job, make_application):
    job = make_job()
    make_job(publish=False)
    make_application(job)

    res = admin_client.get(f'{ADMIN}/overview/')

    assert res.status_code == 200
    data = res.json()
    assert {key: data[key] for key in data if key not in ('recent_users', 'recent_companies')} == {
        'total_users': 4,  # admin, nhà tuyển dụng, 2 ứng viên
        'candidates_count': 2,
        'employers_count': 1,
        'total_companies': 1,
        'pending_companies': Company.objects.filter(verification_status=VerificationStatus.PENDING).count(),
        'total_jobs': 2,
        'published_jobs': 1,
        'total_applications': 1,
    }
    assert [u['email'] for u in data['recent_users']] == list(
        User.objects.order_by('-created_at').values_list('email', flat=True)
    )
    assert set(data['recent_users'][0]) == {'id', 'email', 'full_name', 'role', 'is_active', 'created_at'}
    assert [c['name'] for c in data['recent_companies']] == ['ACME']
    assert set(data['recent_companies'][0]) == {'id', 'name', 'tax_code', 'verification_status', 'created_at'}


def test_overview_lists_at_most_five_recent_users(admin_client):
    User.objects.bulk_create([User(email=f'u{i}@test.com', role=UserRole.CANDIDATE) for i in range(6)])

    assert len(admin_client.get(f'{ADMIN}/overview/').json()['recent_users']) == 5


# ------------------------------------------------------------------------------------------ người dùng
def test_list_users_newest_first(admin_client, admin_user, recruiter, candidate):
    res = admin_client.get(f'{ADMIN}/users/')

    assert res.status_code == 200
    data = res.json()
    assert data['count'] == 3
    assert [u['email'] for u in data['results']] == ['candidate@test.com', 'owner@acme.test', 'admin@test.com']
    first = data['results'][0]
    assert set(first) == USER_FIELDS
    assert first['id'] == str(candidate.user.pk)
    assert (first['role'], first['is_active'], first['is_staff']) == ('candidate', True, False)


def test_filter_users_by_role_and_keyword(admin_client, recruiter, candidate):
    by_role = admin_client.get(f'{ADMIN}/users/', {'role': 'employer'}).json()
    by_email = admin_client.get(f'{ADMIN}/users/', {'q': '  ACME.test '}).json()
    by_name = admin_client.get(f'{ADMIN}/users/', {'q': 'văn a'}).json()
    by_phone = admin_client.get(f'{ADMIN}/users/', {'q': '0912345678'}).json()

    assert [u['email'] for u in by_role['results']] == ['owner@acme.test']
    assert [u['email'] for u in by_email['results']] == ['owner@acme.test']
    assert [u['email'] for u in by_name['results']] == ['candidate@test.com']
    assert [u['email'] for u in by_phone['results']] == ['candidate@test.com']


def test_list_users_returns_newest_100_and_total_count(admin_client):
    User.objects.bulk_create([User(email=f'u{i}@test.com', role=UserRole.CANDIDATE) for i in range(101)])

    data = admin_client.get(f'{ADMIN}/users/').json()

    assert len(data['results']) == 100
    assert data['count'] == 102  # 101 + admin


def test_lock_and_unlock_user(admin_client, candidate):
    url = f'{ADMIN}/users/{candidate.user.pk}/'

    locked = admin_client.patch(url, {'is_active': False}, format='json')
    candidate.user.refresh_from_db()
    assert locked.status_code == 200
    assert set(locked.json()) == USER_FIELDS
    assert locked.json()['is_active'] is False
    assert candidate.user.is_active is False

    unlocked = admin_client.patch(url, {'is_active': True}, format='json')
    candidate.user.refresh_from_db()
    assert unlocked.json()['is_active'] is True
    assert candidate.user.is_active is True


def test_change_user_role(admin_client, candidate):
    res = admin_client.patch(f'{ADMIN}/users/{candidate.user.pk}/', {'role': 'employer'}, format='json')

    candidate.user.refresh_from_db()
    assert res.status_code == 200
    assert res.json()['role'] == 'employer'
    assert candidate.user.role == UserRole.EMPLOYER


def test_update_missing_user(admin_client):
    res = admin_client.patch(f'{ADMIN}/users/{MISSING_ID}/', {'is_active': False}, format='json')

    assert res.status_code == 404
    assert res.json() == {'detail': 'Người dùng không tồn tại.', 'code': 'not_found'}


@pytest.mark.parametrize('payload', [{'role': 'xyz'}, {'is_active': 'abc'}])
def test_update_user_rejects_invalid_values(admin_client, candidate, payload):
    res = admin_client.patch(f'{ADMIN}/users/{candidate.user.pk}/', payload, format='json')

    candidate.user.refresh_from_db()
    assert res.status_code == 400
    assert set(res.json()['errors']) == set(payload)
    assert (candidate.user.role, candidate.user.is_active) == (UserRole.CANDIDATE, True)


def test_form_patch_without_is_active_keeps_account_active(admin_client, candidate):
    # multipart: trường boolean vắng mặt không được hiểu là false (không khóa nhầm tài khoản)
    res = admin_client.patch(f'{ADMIN}/users/{candidate.user.pk}/', {'role': 'employer'}, format='multipart')

    candidate.user.refresh_from_db()
    assert res.status_code == 200
    assert (candidate.user.role, candidate.user.is_active) == (UserRole.EMPLOYER, True)


def test_list_and_detail_urls_only_accept_their_own_methods(admin_client, candidate, recruiter, make_job):
    job = make_job()

    for url in (f'{ADMIN}/users/{candidate.user.pk}/', f'{ADMIN}/companies/{recruiter.company.pk}/',
                f'{ADMIN}/jobs/{job.pk}/'):
        assert admin_client.get(url).status_code == 405
    for url in (f'{ADMIN}/users/', f'{ADMIN}/companies/', f'{ADMIN}/jobs/'):
        assert admin_client.patch(url, {}, format='json').status_code == 405


# ------------------------------------------------------------------------------------------ doanh nghiệp
def test_list_companies(admin_client, recruiter, make_employer):
    make_employer(company_name='Khách sạn Biển Xanh')

    res = admin_client.get(f'{ADMIN}/companies/')

    assert res.status_code == 200
    data = res.json()
    assert data['count'] == 2
    assert [c['name'] for c in data['results']] == ['Khách sạn Biển Xanh', 'ACME']
    acme = data['results'][1]
    assert acme == {
        'id': str(recruiter.company.pk),
        'name': 'ACME',
        'tax_code': '',  # NULL trong DB -> chuỗi rỗng
        'verification_status': recruiter.company.verification_status,
        'phone': '',
        'email': '',
        'website': '',
        'created_at': acme['created_at'],
    }


def test_filter_companies_by_status_and_name(admin_client, recruiter, make_employer):
    other = make_employer(company_name='Khách sạn Biển Xanh').company
    Company.objects.filter(pk=other.pk).update(verification_status=VerificationStatus.VERIFIED)

    by_status = admin_client.get(f'{ADMIN}/companies/', {'status': 'verified'}).json()
    by_name = admin_client.get(f'{ADMIN}/companies/', {'q': ' acm '}).json()

    assert [c['name'] for c in by_status['results']] == ['Khách sạn Biển Xanh']
    assert [c['name'] for c in by_name['results']] == ['ACME']


def test_verify_company(admin_client, recruiter):
    res = admin_client.patch(
        f'{ADMIN}/companies/{recruiter.company.pk}/', {'verification_status': 'verified'}, format='json'
    )

    recruiter.company.refresh_from_db()
    assert res.status_code == 200
    assert res.json() == {'id': str(recruiter.company.pk), 'name': 'ACME', 'verification_status': 'verified'}
    assert recruiter.company.verification_status == VerificationStatus.VERIFIED


@pytest.mark.parametrize('payload', [{'verification_status': 'xyz'}, {'verification_status': None}, {}])
def test_verify_company_rejects_invalid_status(admin_client, recruiter, payload):
    res = admin_client.patch(f'{ADMIN}/companies/{recruiter.company.pk}/', payload, format='json')

    assert res.status_code == 400
    assert res.json()['detail'] == 'Trạng thái không hợp lệ.'
    assert res.json()['code'] == 'validation_error'


def test_update_missing_company(admin_client):
    res = admin_client.patch(f'{ADMIN}/companies/{MISSING_ID}/', {'verification_status': 'verified'}, format='json')

    assert res.status_code == 404
    assert res.json()['detail'] == 'Công ty không tồn tại.'


# ------------------------------------------------------------------------------------------ tin tuyển dụng
def test_list_jobs(admin_client, make_job):
    published = make_job(title='Nhân viên bán hàng')
    draft = make_job(title='Kế toán tổng hợp', publish=False)

    res = admin_client.get(f'{ADMIN}/jobs/')

    assert res.status_code == 200
    data = res.json()
    assert data['count'] == 2
    assert [j['id'] for j in data['results']] == [str(draft.pk), str(published.pk)]
    assert data['results'][1] == {
        'id': str(published.pk),
        'title': 'Nhân viên bán hàng',
        'company_name': 'ACME',
        'status': 'published',
        'job_type': 'full_time',
        'level': 'staff',
        'created_at': data['results'][1]['created_at'],
    }


def test_filter_jobs_by_status_and_title(admin_client, make_job):
    make_job(title='Nhân viên bán hàng')
    make_job(title='Kế toán tổng hợp', publish=False)

    by_status = admin_client.get(f'{ADMIN}/jobs/', {'status': 'draft'}).json()
    by_title = admin_client.get(f'{ADMIN}/jobs/', {'q': ' bán hàng '}).json()

    assert [j['title'] for j in by_status['results']] == ['Kế toán tổng hợp']
    assert [j['title'] for j in by_title['results']] == ['Nhân viên bán hàng']


def test_close_job(admin_client, make_job):
    job = make_job(title='Nhân viên bán hàng')

    res = admin_client.patch(f'{ADMIN}/jobs/{job.pk}/', {'status': 'closed'}, format='json')

    job.refresh_from_db()
    assert res.status_code == 200
    assert res.json() == {'id': str(job.pk), 'title': 'Nhân viên bán hàng', 'status': 'closed'}
    assert job.status == JobStatus.CLOSED


def test_update_job_rejects_invalid_status(admin_client, make_job):
    job = make_job()

    res = admin_client.patch(f'{ADMIN}/jobs/{job.pk}/', {'status': 'xyz'}, format='json')

    assert res.status_code == 400
    assert res.json()['detail'] == 'Trạng thái không hợp lệ.'
    assert Job.objects.get(pk=job.pk).status == JobStatus.PUBLISHED


def test_update_missing_job(admin_client):
    res = admin_client.patch(f'{ADMIN}/jobs/{MISSING_ID}/', {'status': 'closed'}, format='json')

    assert res.status_code == 404
    assert res.json()['detail'] == 'Tin tuyển dụng không tồn tại.'
