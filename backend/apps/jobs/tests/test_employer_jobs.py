from datetime import timedelta

import pytest
from django.test import override_settings
from django.utils import timezone

from apps.employers.models import VerificationStatus
from apps.jobs import signals
from apps.jobs.models import Job, JobStatus
from conftest import client_for

pytestmark = pytest.mark.django_db

JOBS = '/api/v1/employer/jobs/'


def detail_url(job_id, action=None):
    return f'{JOBS}{job_id}/' + (f'{action}/' if action else '')


def expire(job):
    """Giả lập tin đã qua hạn nộp (validate API không cho đặt deadline trong quá khứ)."""
    Job.objects.filter(pk=job.pk).update(deadline=timezone.localdate() - timedelta(days=1))


# ---------------------------------------------------------------- tạo / sửa
def test_create_draft_job(employer_client, job_payload, recruiter):
    res = employer_client.post(JOBS, job_payload(), format='json')

    assert res.status_code == 201
    data = res.data
    assert data['status'] == 'draft'
    assert data['published_at'] is None
    assert [s['name'] for s in data['skills']] == ['Python', 'Django']
    assert data['location']['name'] == 'Hà Nội'
    assert data['company']['id'] == str(recruiter.company.id)
    assert data['created_by']['id'] == str(recruiter.user.id)
    assert data['allowed_actions'] == ['publish', 'delete']
    assert data['slug'].startswith('backend-developer-python-')


def test_create_and_publish_immediately(employer_client, job_payload):
    res = employer_client.post(JOBS, job_payload(status='published'), format='json')

    assert res.status_code == 201
    assert res.data['status'] == 'published'
    assert res.data['published_at'] is not None
    assert res.data['allowed_actions'] == ['pause', 'close', 'delete']


def test_publish_requires_at_least_one_skill(employer_client, job_payload):
    res = employer_client.post(JOBS, job_payload(status='published', skills=[]), format='json')

    assert res.status_code == 400
    assert res.data['code'] == 'skills_required'
    assert not Job.objects.exists()  # cả thao tác tạo bị rollback


@pytest.mark.parametrize(
    'overrides, field',
    [
        ({'title': '   '}, 'title'),
        ({'salary_min': 30_000_000, 'salary_max': 10_000_000}, 'salary_max'),
        ({'salary_min': -1}, 'salary_min'),
        ({'job_type': 'remote'}, 'job_type'),
        ({'level': 'god'}, 'level'),
        ({'headcount': 0}, 'headcount'),
        ({'location_id': 9999}, 'location_id'),
        ({'skills': [{'name': ''}]}, 'skills'),
        ({'skills': [{'name': 'Python', 'weight': 9}]}, 'skills'),
    ],
)
def test_create_validation(employer_client, job_payload, overrides, field):
    res = employer_client.post(JOBS, job_payload(**overrides), format='json')

    assert res.status_code == 400
    assert field in res.data['errors']
    assert res.data['detail']  # thông điệp đầu tiên để frontend hiển thị


def test_deadline_must_not_be_in_the_past(employer_client, job_payload):
    yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()

    res = employer_client.post(JOBS, job_payload(deadline=yesterday), format='json')

    assert res.status_code == 400
    assert res.data['errors']['deadline'] == ['Hạn nộp hồ sơ phải từ hôm nay trở đi.']


def test_partial_update_checks_salary_against_current_values(employer_client, make_job):
    job = make_job(salary_min=20_000_000, salary_max=30_000_000)

    res = employer_client.patch(detail_url(job.id), {'salary_max': 10_000_000}, format='json')

    assert res.status_code == 400
    assert 'salary_max' in res.data['errors']


def test_update_content_and_replace_skills(employer_client, make_job):
    job = make_job(skills=('Python', 'Django'))

    res = employer_client.patch(
        detail_url(job.id),
        {'title': 'Senior Python Developer', 'skills': [{'name': 'FastAPI', 'is_required': False}, {'name': 'python'}]},
        format='json',
    )

    assert res.status_code == 200
    assert res.data['title'] == 'Senior Python Developer'
    assert [(s['name'], s['is_required']) for s in res.data['skills']] == [('FastAPI', False), ('Python', True)]


def test_editing_expired_job_without_touching_deadline_is_allowed(employer_client, make_job):
    job = make_job()
    expire(job)

    res = employer_client.patch(
        detail_url(job.id), {'title': 'Sửa lỗi chính tả', 'deadline': (timezone.localdate() - timedelta(days=1)).isoformat()},
        format='json',
    )

    assert res.status_code == 200


def test_status_cannot_be_changed_via_patch(employer_client, make_job):
    job = make_job(publish=False)

    res = employer_client.patch(detail_url(job.id), {'status': 'published'}, format='json')

    assert res.status_code == 400
    assert 'status' in res.data['errors']


def test_put_is_not_allowed(employer_client, make_job, job_payload):
    job = make_job()
    assert employer_client.put(detail_url(job.id), job_payload(), format='json').status_code == 405


# ---------------------------------------------------------------- danh sách
def test_list_only_contains_own_company_jobs(employer_client, make_job, other_recruiter):
    own = make_job(title='Tin của ACME')
    make_job(company=other_recruiter.company, created_by=other_recruiter.user, title='Tin công ty khác')

    res = employer_client.get(JOBS)

    assert res.status_code == 200
    assert res.data['count'] == 1
    assert res.data['results'][0]['id'] == str(own.id)
    assert {'count', 'total_pages', 'page', 'page_size', 'results'} <= res.data.keys()


def test_cannot_access_other_company_job(employer_client, make_job, other_recruiter):
    other_job = make_job(company=other_recruiter.company, created_by=other_recruiter.user)

    assert employer_client.get(detail_url(other_job.id)).status_code == 404
    assert employer_client.patch(detail_url(other_job.id), {'title': 'x'}, format='json').status_code == 404
    assert employer_client.delete(detail_url(other_job.id)).status_code == 404
    assert employer_client.post(detail_url(other_job.id, 'close')).status_code == 404


def test_member_recruiter_manages_company_jobs(member, make_job):
    job = make_job()

    res = client_for(member.user).post(detail_url(job.id, 'pause'))

    assert res.status_code == 200


def test_filter_search_order_and_paginate(employer_client, make_job):
    make_job(title='Python Developer')
    make_job(title='Java Developer')
    make_job(title='Python Intern', publish=False)
    closed = make_job(title='Tester')
    employer_client.post(detail_url(closed.id, 'close'))

    def titles(query):
        return [j['title'] for j in employer_client.get(JOBS + query).data['results']]

    assert titles('?status=draft') == ['Python Intern']
    assert titles('?status=closed') == ['Tester']
    assert set(titles('?status=published')) == {'Python Developer', 'Java Developer'}
    assert set(titles('?q=python')) == {'Python Developer', 'Python Intern'}
    assert titles('?ordering=title') == ['Java Developer', 'Python Developer', 'Python Intern', 'Tester']
    page = employer_client.get(JOBS + '?page_size=3&page=2').data
    assert (page['count'], page['total_pages'], page['page'], len(page['results'])) == (4, 2, 2, 1)


def test_list_counts_applicants(employer_client, make_job, make_application):
    job = make_job()
    make_application(job)
    make_application(job, statuses=['screening'])

    item = employer_client.get(JOBS).data['results'][0]

    assert (item['applicant_count'], item['new_applicant_count']) == (2, 1)
    assert 'delete' not in item['allowed_actions']


# ---------------------------------------------------------------- trạng thái
def test_status_lifecycle(employer_client, make_job):
    job = make_job(publish=False)

    def act(action):
        return employer_client.post(detail_url(job.id, action))

    assert act('publish').data['status'] == 'published'
    paused = act('pause').data
    assert paused['status'] == 'paused' and paused['allowed_actions'] == ['publish', 'close', 'delete']
    assert act('publish').data['status'] == 'published'  # tiếp tục tuyển
    closed = act('close').data
    assert closed['status'] == 'closed' and closed['closed_at'] is not None
    reopened = act('publish').data  # mở lại
    assert reopened['status'] == 'published' and reopened['closed_at'] is None


@pytest.mark.parametrize('action', ['pause', 'close'])
def test_invalid_transition_from_draft(employer_client, make_job, action):
    job = make_job(publish=False)

    res = employer_client.post(detail_url(job.id, action))

    assert res.status_code == 409
    assert res.data['code'] == 'invalid_status_transition'
    assert 'Bản nháp' in res.data['detail']


def test_expired_status_is_derived_from_deadline(employer_client, make_job):
    job = make_job()
    expire(job)

    data = employer_client.get(detail_url(job.id)).data
    assert data['status'] == 'expired'
    assert data['allowed_actions'] == ['close', 'delete']
    assert [j['id'] for j in employer_client.get(JOBS + '?status=expired').data['results']] == [str(job.id)]
    assert employer_client.get(JOBS + '?status=published').data['count'] == 0
    assert employer_client.post(detail_url(job.id, 'pause')).status_code == 409

    # Gia hạn -> tự động đang tuyển trở lại
    new_deadline = (timezone.localdate() + timedelta(days=10)).isoformat()
    assert employer_client.patch(detail_url(job.id), {'deadline': new_deadline}, format='json').data['status'] == 'published'


def test_reopen_closed_job_with_past_deadline_requires_new_deadline(employer_client, make_job):
    job = make_job()
    employer_client.post(detail_url(job.id, 'close'))
    expire(job)

    res = employer_client.post(detail_url(job.id, 'publish'))

    assert res.status_code == 400
    assert res.data['code'] == 'deadline_passed'


@override_settings(EMPLOYER_REQUIRE_VERIFIED_COMPANY=True)
def test_publish_requires_verified_company_when_enabled(employer_client, make_job, recruiter):
    job = make_job(publish=False)

    res = employer_client.post(detail_url(job.id, 'publish'))
    assert res.status_code == 403
    assert res.data['code'] == 'company_not_verified'

    recruiter.company.verification_status = VerificationStatus.VERIFIED
    recruiter.company.save()
    assert employer_client.post(detail_url(job.id, 'publish')).status_code == 200


# ---------------------------------------------------------------- xóa
def test_delete_job_without_applications_is_soft_delete(employer_client, make_job):
    job = make_job()

    assert employer_client.delete(detail_url(job.id)).status_code == 204
    assert employer_client.get(detail_url(job.id)).status_code == 404
    assert Job.all_objects.get(pk=job.pk).deleted_at is not None


def test_cannot_delete_job_with_applications(employer_client, make_job, make_application):
    job = make_job()
    make_application(job)

    res = employer_client.delete(detail_url(job.id))

    assert res.status_code == 409
    assert res.data['code'] == 'job_has_applications'
    assert Job.objects.filter(pk=job.pk).exists()


# ---------------------------------------------------------------- domain event (điểm mở rộng cho AI)
def test_domain_events_are_sent_after_commit(employer_client, make_job, django_capture_on_commit_callbacks):
    received = []

    def receiver(signal, **kwargs):
        received.append((signal, kwargs['job'].title))

    for sig in (signals.job_published, signals.job_updated, signals.job_unpublished, signals.job_deleted):
        sig.connect(receiver, dispatch_uid=f'test-{id(sig)}')
    try:
        job = make_job(publish=False, title='Tin A')
        with django_capture_on_commit_callbacks(execute=True):
            employer_client.post(detail_url(job.id, 'publish'))
        with django_capture_on_commit_callbacks(execute=True):
            employer_client.patch(detail_url(job.id), {'title': 'Tin B'}, format='json')
        with django_capture_on_commit_callbacks(execute=True):
            employer_client.post(detail_url(job.id, 'close'))
        with django_capture_on_commit_callbacks(execute=True):
            employer_client.delete(detail_url(job.id))
    finally:
        for sig in (signals.job_published, signals.job_updated, signals.job_unpublished, signals.job_deleted):
            sig.disconnect(dispatch_uid=f'test-{id(sig)}')

    assert received == [
        (signals.job_published, 'Tin A'),
        (signals.job_updated, 'Tin B'),
        (signals.job_unpublished, 'Tin B'),
        (signals.job_deleted, 'Tin B'),
    ]
    assert JobStatus.CLOSED == Job.all_objects.get(pk=job.pk).status
