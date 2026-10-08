from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.candidates.models import CandidateProfile
from conftest import PASSWORD, client_for

pytestmark = pytest.mark.django_db

REGISTER = '/api/v1/candidate/register/'
PROFILE = '/api/v1/candidate/profile/'


def register_payload(**overrides):
    data = {
        'full_name': 'Lê Thị Cúc',
        'email': 'Cuc.Le@Example.com',
        'password': PASSWORD,
        'phone': '0901 111 220',
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------- đăng ký
def test_register_candidate_creates_user_and_empty_profile(api_client):
    res = api_client.post(REGISTER, register_payload(), format='json')

    assert res.status_code == 201
    assert {'access', 'refresh', 'user'} <= res.data.keys()
    user = User.objects.get(email='cuc.le@example.com')  # email được chuẩn hóa chữ thường
    assert user.role == UserRole.CANDIDATE
    assert user.candidate_profile.headline == ''
    profile = res.data['user']['profile']
    assert profile == {
        'candidate_id': str(user.candidate_profile.id), 'headline': '', 'is_open_to_work': True, 'cv_count': 0,
    }


def test_registered_candidate_can_login(api_client):
    api_client.post(REGISTER, register_payload(), format='json')

    res = api_client.post('/api/v1/auth/login/', {'email': 'cuc.le@example.com', 'password': PASSWORD}, format='json')

    assert res.status_code == 200
    assert res.data['user']['role'] == 'candidate'
    assert res.data['user']['profile']['cv_count'] == 0


def test_register_ignores_stale_token(api_client):
    api_client.credentials(HTTP_AUTHORIZATION='Bearer token-het-han')

    assert api_client.post(REGISTER, register_payload(), format='json').status_code == 201


def test_register_rejects_duplicate_email_across_roles(api_client, recruiter):
    res = api_client.post(REGISTER, register_payload(email='OWNER@acme.test'), format='json')

    assert res.status_code == 400
    assert res.data['errors']['email'] == ['Email đã được sử dụng.']


def test_register_rejects_weak_password(api_client):
    res = api_client.post(REGISTER, register_payload(password='12345678'), format='json')

    assert res.status_code == 400
    assert 'password' in res.data['errors']
    assert not User.objects.exists()


@pytest.mark.parametrize('field', ['full_name', 'email', 'password'])
def test_register_required_fields(api_client, field):
    res = api_client.post(REGISTER, register_payload(**{field: ''}), format='json')

    assert res.status_code == 400
    assert field in res.data['errors']


# ---------------------------------------------------------------- phân quyền
def test_employer_cannot_use_candidate_api(employer_client):
    res = employer_client.get(PROFILE)

    assert res.status_code == 403
    assert res.data['detail'] == 'Chức năng này chỉ dành cho ứng viên.'


def test_candidate_cannot_use_employer_api(candidate_client):
    assert candidate_client.get('/api/v1/employer/company/').status_code == 403


def test_candidate_without_profile_is_forbidden(db):
    user = User.objects.create_user(email='noprofile@test.com', password=PASSWORD, role=UserRole.CANDIDATE)

    res = client_for(user).get(PROFILE)

    assert res.status_code == 403
    assert 'chưa có hồ sơ' in res.data['detail']


def test_profile_requires_authentication(api_client):
    assert api_client.get(PROFILE).status_code == 401


# ---------------------------------------------------------------- hồ sơ
def test_get_profile(candidate_client, candidate):
    res = candidate_client.get(PROFILE)

    assert res.status_code == 200
    assert res.data['id'] == str(candidate.id)
    assert (res.data['full_name'], res.data['email'], res.data['phone']) == (
        'Nguyễn Văn A', 'candidate@test.com', '0912345678',
    )
    assert res.data['is_open_to_work'] is True and res.data['is_public'] is False


def test_update_profile(candidate_client, candidate):
    res = candidate_client.patch(
        PROFILE,
        {
            'full_name': ' Nguyễn Văn An ', 'phone': '0987654321', 'headline': 'Backend Developer | 3 năm Python',
            'date_of_birth': '2000-05-20', 'gender': 'male', 'location_id': 1, 'summary': 'Giới thiệu',
            'years_of_experience': 3, 'current_level': 'middle', 'desired_position': 'Backend Developer',
            'desired_salary_min': 25_000_000, 'desired_salary_max': 35_000_000, 'desired_job_type': 'full_time',
            'desired_work_mode': 'hybrid', 'is_public': True,
        },
        format='json',
    )

    assert res.status_code == 200, res.data
    assert res.data['full_name'] == 'Nguyễn Văn An'
    assert res.data['location']['name'] == 'Hà Nội'
    assert res.data['years_of_experience'] == 3
    profile = CandidateProfile.objects.get(pk=candidate.pk)
    assert (profile.user.phone, profile.current_level, profile.is_public) == ('0987654321', 'middle', True)
    # Thông tin hiển thị lên /auth/me/
    assert candidate_client.get('/api/v1/auth/me/').data['profile']['headline'] == 'Backend Developer | 3 năm Python'


@pytest.mark.parametrize(
    'payload, field',
    [
        ({'full_name': ''}, 'full_name'),
        ({'phone': 'abc'}, 'phone'),
        ({'desired_salary_min': 30_000_000, 'desired_salary_max': 10_000_000}, 'desired_salary_max'),
        ({'desired_salary_min': -1}, 'desired_salary_min'),
        ({'years_of_experience': -1}, 'years_of_experience'),
        ({'current_level': 'god'}, 'current_level'),
        ({'desired_work_mode': 'space'}, 'desired_work_mode'),
        ({'salary_currency': 'EUR'}, 'salary_currency'),
        ({'location_id': 9999}, 'location_id'),
        ({'gender': 'x'}, 'gender'),
    ],
)
def test_update_profile_validation(candidate_client, payload, field):
    res = candidate_client.patch(PROFILE, payload, format='json')

    assert res.status_code == 400
    assert field in res.data['errors']


def test_partial_update_checks_salary_against_current_values(candidate_client):
    candidate_client.patch(PROFILE, {'desired_salary_min': 20_000_000, 'desired_salary_max': 30_000_000}, format='json')

    res = candidate_client.patch(PROFILE, {'desired_salary_max': 10_000_000}, format='json')

    assert res.status_code == 400
    assert 'desired_salary_max' in res.data['errors']


@pytest.mark.parametrize('years_ago', [0, 14, 101])
def test_date_of_birth_must_be_plausible(candidate_client, years_ago):
    dob = timezone.localdate() - timedelta(days=365 * years_ago + 1)

    res = candidate_client.patch(PROFILE, {'date_of_birth': dob.isoformat()}, format='json')

    assert res.status_code == 400
    assert 'date_of_birth' in res.data['errors']


def test_email_is_read_only(candidate_client, candidate):
    candidate_client.patch(PROFILE, {'email': 'hacker@test.com'}, format='json')

    candidate.user.refresh_from_db()
    assert candidate.user.email == 'candidate@test.com'
