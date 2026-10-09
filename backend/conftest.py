"""Fixture pytest dùng chung: nhà tuyển dụng, ứng viên, API client đã đăng nhập, factory tạo tin / CV / hồ sơ."""
import io
import itertools
import zipfile
from datetime import timedelta
from xml.sax.saxutils import escape

import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.applications import services as application_services
from apps.applications.management.commands.seed_demo import build_pdf
from apps.candidates import services as candidate_services
from apps.candidates.models import CandidateProfile
from apps.cvs.models import CV, CVMimeType
from apps.employers import services as employer_services
from apps.employers.models import CompanyRole, Recruiter, RecruiterStatus
from apps.jobs import services as job_services

PASSWORD = 'S3cure-pass!2026'
_seq = itertools.count(1)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_employer(db):
    def factory(email=None, company_name='Công ty Demo', password=PASSWORD, **kwargs):
        n = next(_seq)
        return employer_services.register_employer(
            email=email or f'employer{n}@test.com', password=password, full_name=f'Nhà tuyển dụng {n}',
            company_name=company_name, **kwargs,
        )

    return factory


@pytest.fixture
def recruiter(make_employer):
    """Owner của công ty ACME."""
    return make_employer(email='owner@acme.test', company_name='ACME')


@pytest.fixture
def member(recruiter):
    """Recruiter thường (member) cùng công ty ACME."""
    user = User.objects.create_user(email='member@acme.test', password=PASSWORD, role=UserRole.EMPLOYER,
                                    full_name='Thành viên')
    return Recruiter.objects.create(user=user, company=recruiter.company, company_role=CompanyRole.MEMBER,
                                    status=RecruiterStatus.ACTIVE)


def client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def employer_client(recruiter):
    return client_for(recruiter.user)


@pytest.fixture
def other_recruiter(make_employer):
    return make_employer(email='owner@other.test', company_name='Other Corp')


@pytest.fixture
def future_date():
    return lambda days=30: timezone.localdate() + timedelta(days=days)


@pytest.fixture
def job_payload(future_date):
    def factory(**overrides):
        data = {
            'title': 'Backend Developer (Python)',
            'description': 'Phát triển API.',
            'requirements': '2 năm Python\nBiết Django',
            'benefits': 'Lương tháng 13',
            'job_type': 'full_time',
            'work_mode': 'hybrid',
            'level': 'middle',
            'salary_min': 20_000_000,
            'salary_max': 30_000_000,
            'location_id': 1,
            'deadline': future_date().isoformat(),
            'skills': [{'name': 'Python'}, {'name': 'Django'}],
        }
        data.update(overrides)
        return data

    return factory


@pytest.fixture
def make_job(recruiter, future_date):
    def factory(company=None, created_by=None, publish=True, skills=('Python', 'Django'), **overrides):
        data = {
            'title': 'Python Developer',
            'description': 'Mô tả',
            'requirements': 'Yêu cầu',
            'job_type': 'full_time',
            'level': 'junior',
            'deadline': future_date(),
        }
        data.update(overrides)
        return job_services.create_job(
            company=company or recruiter.company,
            created_by=created_by or recruiter.user,
            data=data,
            skills=[{'name': s} for s in skills],
            publish=publish,
        )

    return factory


@pytest.fixture
def make_candidate(db):
    def factory(full_name='Nguyễn Văn A', headline='Python Developer'):
        n = next(_seq)
        user = User.objects.create_user(email=f'candidate{n}@test.com', password=None, role=UserRole.CANDIDATE,
                                        full_name=full_name, phone='0912345678')
        profile = CandidateProfile.objects.create(user=user, headline=headline, years_of_experience=2)
        content = b'%PDF-1.4 test cv'
        cv = CV(candidate=profile, title='CV', original_filename=f'CV {full_name}.pdf', mime_type=CVMimeType.PDF,
                file_size=len(content), file_hash='0' * 64)
        cv.file.save('cv.pdf', ContentFile(content), save=False)
        cv.save()
        return profile, cv

    return factory


@pytest.fixture
def make_application(make_candidate, recruiter):
    def factory(job, candidate=None, statuses=(), **candidate_kwargs):
        profile, cv = candidate or make_candidate(**candidate_kwargs)
        application = application_services.submit_application(candidate=profile, job=job, cv=cv)
        for status in statuses:
            application = application_services.change_status(application, to_status=status, by=recruiter.user)
        return application

    return factory


# ------------------------------------------------------------------------------------------ ứng viên & CV
@pytest.fixture
def candidate(db):
    """Ứng viên đăng ký qua service như API thật (chưa có CV)."""
    return candidate_services.register_candidate(
        email='candidate@test.com', password=PASSWORD, full_name='Nguyễn Văn A', phone='0912345678'
    )


@pytest.fixture
def candidate_client(candidate):
    return client_for(candidate.user)


def pdf_bytes(*lines: str) -> bytes:
    """PDF 1 trang có lớp chữ (font chuẩn nên tiếng Việt bị bỏ dấu); không truyền dòng nào = PDF 'scan'."""
    return build_pdf([('text', line) for line in lines])


def docx_bytes(*paragraphs: str, header: str = '') -> bytes:
    """DOCX tối giản đúng cấu trúc Office Open XML (giữ nguyên tiếng Việt có dấu)."""
    ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'

    def body(items):
        return ''.join(f'<w:p><w:r><w:t xml:space="preserve">{escape(p)}</w:t></w:r></w:p>' for p in items)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            '[Content_Types].xml',
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/'
            'content-types"><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/'
            'document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.'
            'main+xml"/></Types>',
        )
        archive.writestr('word/document.xml', f'<?xml version="1.0" encoding="UTF-8"?><w:document {ns}><w:body>'
                                              f'{body(paragraphs)}</w:body></w:document>')
        if header:
            archive.writestr('word/header1.xml', f'<?xml version="1.0" encoding="UTF-8"?><w:hdr {ns}>'
                                                 f'{body([header])}</w:hdr>')
    return buffer.getvalue()


@pytest.fixture
def cv_upload():
    """Factory file CV để gửi multipart. Mỗi file có nội dung khác nhau (không bị coi là trùng)."""

    def factory(kind='pdf', name=None, text='Kinh nghiem 2 nam Python, Django, PostgreSQL. Email: a@test.com'):
        unique = f'{text} (ma {next(_seq)})'
        if kind == 'pdf':
            return SimpleUploadedFile(name or 'cv.pdf', pdf_bytes(unique), content_type='application/pdf')
        return SimpleUploadedFile(
            name or 'cv.docx', docx_bytes(unique),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

    return factory
