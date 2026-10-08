import pytest

from conftest import PASSWORD

pytestmark = pytest.mark.django_db

LOGIN = '/api/v1/auth/login/'


def login(api_client, email='owner@acme.test', password=PASSWORD):
    return api_client.post(LOGIN, {'email': email, 'password': password}, format='json')


def test_login_returns_tokens_and_employer_profile(api_client, recruiter):
    res = login(api_client, email='OWNER@Acme.test')  # email không phân biệt hoa thường

    assert res.status_code == 200
    assert {'access', 'refresh', 'user'} <= res.data.keys()
    user = res.data['user']
    assert user['role'] == 'employer'
    assert user['profile']['company_role'] == 'owner'
    assert user['profile']['company']['name'] == 'ACME'


def test_login_with_wrong_password(api_client, recruiter):
    res = login(api_client, password='sai-mat-khau')

    assert res.status_code == 401
    assert res.data == {'detail': 'Email hoặc mật khẩu không đúng.', 'code': 'no_active_account'}


def test_inactive_user_cannot_login(api_client, recruiter):
    recruiter.user.is_active = False
    recruiter.user.save()

    assert login(api_client).status_code == 401


def test_me_requires_authentication(api_client):
    res = api_client.get('/api/v1/auth/me/')

    assert res.status_code == 401
    assert res.data['code'] == 'not_authenticated'


def test_me_with_bearer_token(api_client, recruiter):
    access = login(api_client).data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    res = api_client.get('/api/v1/auth/me/')

    assert res.status_code == 200
    assert res.data['email'] == 'owner@acme.test'


def test_update_me(employer_client):
    res = employer_client.patch('/api/v1/auth/me/', {'full_name': ' Trần Bình ', 'phone': '0987654321'}, format='json')

    assert res.status_code == 200
    assert res.data['full_name'] == 'Trần Bình'
    assert res.data['phone'] == '0987654321'


def test_update_me_rejects_invalid_phone(employer_client):
    res = employer_client.patch('/api/v1/auth/me/', {'phone': 'abc'}, format='json')

    assert res.status_code == 400
    assert 'phone' in res.data['errors']


def test_refresh_rotates_and_blacklists_old_token(api_client, recruiter):
    refresh = login(api_client).data['refresh']

    first = api_client.post('/api/v1/auth/token/refresh/', {'refresh': refresh}, format='json')
    reused = api_client.post('/api/v1/auth/token/refresh/', {'refresh': refresh}, format='json')

    assert first.status_code == 200
    assert {'access', 'refresh'} <= first.data.keys()
    assert reused.status_code == 401


def test_logout_blacklists_refresh_token(api_client, recruiter):
    refresh = login(api_client).data['refresh']

    res = api_client.post('/api/v1/auth/logout/', {'refresh': refresh}, format='json')

    assert res.status_code == 204
    assert api_client.post('/api/v1/auth/token/refresh/', {'refresh': refresh}, format='json').status_code == 401


def test_logout_with_invalid_token(api_client):
    res = api_client.post('/api/v1/auth/logout/', {'refresh': 'khong-hop-le'}, format='json')

    assert res.status_code == 400
    assert 'refresh' in res.data['errors']


def test_change_password_revokes_old_sessions(api_client, recruiter):
    tokens = login(api_client).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    res = api_client.post(
        '/api/v1/auth/change-password/',
        {'current_password': PASSWORD, 'new_password': 'Mat-khau-moi-2026'},
        format='json',
    )

    assert res.status_code == 200
    assert {'access', 'refresh'} <= res.data.keys()
    # refresh token cũ bị thu hồi, mật khẩu mới dùng được
    assert api_client.post('/api/v1/auth/token/refresh/', {'refresh': tokens['refresh']}, format='json').status_code == 401
    api_client.credentials()
    assert login(api_client, password='Mat-khau-moi-2026').status_code == 200


def test_change_password_with_wrong_current_password(employer_client):
    res = employer_client.post(
        '/api/v1/auth/change-password/',
        {'current_password': 'sai', 'new_password': 'Mat-khau-moi-2026'},
        format='json',
    )

    assert res.status_code == 400
    assert res.data['errors'] == {'current_password': ['Mật khẩu hiện tại không đúng.']}


def test_change_password_validates_strength(employer_client):
    res = employer_client.post(
        '/api/v1/auth/change-password/', {'current_password': PASSWORD, 'new_password': '123'}, format='json'
    )

    assert res.status_code == 400
