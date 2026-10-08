"""Fixture pytest dùng chung: nhà tuyển dụng, API client đã đăng nhập, factory tạo tin / ứng viên / hồ sơ."""
import itertools
from datetime import timedelta

import pytest
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.applications import services as application_services
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
