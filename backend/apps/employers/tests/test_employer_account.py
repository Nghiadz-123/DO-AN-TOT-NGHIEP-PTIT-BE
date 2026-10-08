import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.accounts.models import User, UserRole
from apps.employers.models import Company, CompanyRole, VerificationStatus
from conftest import PASSWORD, client_for

pytestmark = pytest.mark.django_db

REGISTER = '/api/v1/employer/register/'
COMPANY = '/api/v1/employer/company/'


def register_payload(**overrides):
    data = {
        'full_name': 'Trần Thị Bình',
        'email': 'Binh.Tran@Example.com',
        'password': PASSWORD,
        'phone': '0987 654 321',
        'company_name': ' TechViet Solutions ',
        'position': 'HR Manager',
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------- đăng ký
def test_register_employer_creates_user_company_and_owner(api_client):
    res = api_client.post(REGISTER, register_payload(), format='json')

    assert res.status_code == 201
    assert {'access', 'refresh', 'user'} <= res.data.keys()
    user = User.objects.get(email='binh.tran@example.com')  # email được chuẩn hóa chữ thường
    assert user.role == UserRole.EMPLOYER
    recruiter = user.recruiter
    assert recruiter.company_role == CompanyRole.OWNER
    assert recruiter.status == 'active'
    assert recruiter.company.name == 'TechViet Solutions'
    assert recruiter.company.verification_status == VerificationStatus.PENDING
    assert res.data['user']['profile']['company']['name'] == 'TechViet Solutions'


def test_register_rejects_duplicate_email(api_client, recruiter):
    res = api_client.post(REGISTER, register_payload(email='OWNER@acme.test'), format='json')

    assert res.status_code == 400
    assert res.data['errors']['email'] == ['Email đã được sử dụng.']


def test_register_rejects_weak_password(api_client):
    res = api_client.post(REGISTER, register_payload(password='12345678'), format='json')

    assert res.status_code == 400
    assert 'password' in res.data['errors']
    assert not User.objects.exists()


def test_register_requires_company_name(api_client):
    res = api_client.post(REGISTER, register_payload(company_name=''), format='json')

    assert res.status_code == 400
    assert 'company_name' in res.data['errors']


# ---------------------------------------------------------------- phân quyền
def test_candidate_cannot_use_employer_api(make_candidate):
    profile, _ = make_candidate()

    res = client_for(profile.user).get(COMPANY)

    assert res.status_code == 403
    assert res.data['detail'] == 'Chức năng này chỉ dành cho nhà tuyển dụng.'


def test_employer_without_active_recruiter_is_forbidden(recruiter):
    recruiter.status = 'removed'
    recruiter.save()

    res = client_for(recruiter.user).get(COMPANY)

    assert res.status_code == 403
    assert 'chưa được kích hoạt' in res.data['detail']


# ---------------------------------------------------------------- hồ sơ công ty
def test_get_and_update_company(employer_client):
    res = employer_client.patch(
        COMPANY,
        {
            'name': 'ACME Việt Nam', 'tax_code': '0101234567', 'website': 'https://acme.vn', 'location_id': 1,
            'industry_id': 1, 'company_size': '51-200', 'founded_year': 2015, 'description': 'Giới thiệu',
        },
        format='json',
    )

    assert res.status_code == 200
    assert res.data['name'] == 'ACME Việt Nam'
    assert res.data['location']['name'] == 'Hà Nội'
    assert res.data['industry']['id'] == 1
    assert employer_client.get(COMPANY).data['tax_code'] == '0101234567'


def test_member_can_view_but_not_update_company(member):
    client = client_for(member.user)

    assert client.get(COMPANY).status_code == 200
    res = client.patch(COMPANY, {'name': 'Đổi tên'}, format='json')
    assert res.status_code == 403


@pytest.mark.parametrize('tax_code', ['123', '01012345678', 'abcdefghij'])
def test_invalid_tax_code(employer_client, tax_code):
    res = employer_client.patch(COMPANY, {'tax_code': tax_code}, format='json')

    assert res.status_code == 400
    assert 'tax_code' in res.data['errors']


def test_tax_code_must_be_unique_even_against_deleted_company(employer_client, other_recruiter):
    other = other_recruiter.company
    other.tax_code = '0101234567'
    other.save()
    other.soft_delete()

    res = employer_client.patch(COMPANY, {'tax_code': '0101234567'}, format='json')

    assert res.status_code == 400
    assert res.data['errors']['tax_code'] == ['Mã số thuế đã được đăng ký bởi công ty khác.']


def test_blank_tax_code_is_stored_as_null(employer_client, other_recruiter):
    assert employer_client.patch(COMPANY, {'tax_code': ''}, format='json').status_code == 200
    # 2 công ty cùng để trống MST không bị trùng unique
    assert client_for(other_recruiter.user).patch(COMPANY, {'tax_code': ''}, format='json').status_code == 200
    assert Company.objects.filter(tax_code__isnull=True).count() == 2


def test_changing_tax_code_of_verified_company_requires_reverification(employer_client, recruiter):
    company = recruiter.company
    company.verification_status = VerificationStatus.VERIFIED
    company.save()

    employer_client.patch(COMPANY, {'description': 'Không ảnh hưởng xác minh'}, format='json')
    company.refresh_from_db()
    assert company.verification_status == VerificationStatus.VERIFIED

    employer_client.patch(COMPANY, {'tax_code': '0109999999'}, format='json')
    company.refresh_from_db()
    assert company.verification_status == VerificationStatus.PENDING


def test_verification_status_is_read_only(employer_client, recruiter):
    employer_client.patch(COMPANY, {'verification_status': 'verified'}, format='json')

    recruiter.company.refresh_from_db()
    assert recruiter.company.verification_status == VerificationStatus.PENDING


# ---------------------------------------------------------------- logo
def png_file(name='logo.png', size=(32, 32)):
    buffer = io.BytesIO()
    Image.new('RGB', size, 'blue').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


def test_upload_and_remove_logo(employer_client, recruiter):
    res = employer_client.post(f'{COMPANY}logo/', {'logo': png_file()}, format='multipart')

    assert res.status_code == 200
    assert res.data['logo_url'].startswith('http://testserver/media/companies/')
    recruiter.company.refresh_from_db()
    stored = recruiter.company.logo.name
    assert recruiter.company.logo.storage.exists(stored)

    res = employer_client.delete(f'{COMPANY}logo/')
    assert res.status_code == 200
    assert res.data['logo_url'] is None
    assert not recruiter.company.logo.storage.exists(stored)


def test_upload_logo_rejects_non_image(employer_client):
    fake = SimpleUploadedFile('logo.png', b'not an image', content_type='image/png')

    res = employer_client.post(f'{COMPANY}logo/', {'logo': fake}, format='multipart')

    assert res.status_code == 400
    assert 'logo' in res.data['errors']


# ---------------------------------------------------------------- hồ sơ recruiter
def test_get_and_update_recruiter_profile(employer_client, recruiter):
    res = employer_client.patch(
        '/api/v1/employer/profile/', {'full_name': 'Bình Trần', 'phone': '0911222333', 'position': 'Head of HR'},
        format='json',
    )

    assert res.status_code == 200
    assert res.data['full_name'] == 'Bình Trần'
    assert res.data['phone'] == '0911222333'
    assert res.data['position'] == 'Head of HR'
    assert res.data['company_role'] == 'owner'
    assert User.objects.get(pk=recruiter.user.pk).full_name == 'Bình Trần'


def test_profile_rejects_blank_name(employer_client):
    res = employer_client.patch('/api/v1/employer/profile/', {'full_name': ''}, format='json')

    assert res.status_code == 400
    assert 'full_name' in res.data['errors']
