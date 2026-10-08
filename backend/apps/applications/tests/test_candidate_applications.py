import uuid

import pytest

from apps.applications import services, signals
from apps.applications.models import Application
from apps.cvs import services as cv_services
from apps.cvs.models import CVMimeType
from apps.jobs import services as job_services
from conftest import client_for, pdf_bytes

pytestmark = pytest.mark.django_db

APPS = '/api/v1/candidate/applications/'


def url(application_id, action=None):
    return f'{APPS}{application_id}/' + (f'{action}/' if action else '')


@pytest.fixture
def make_cv(candidate):
    """CV tải lên qua đúng service của API upload."""

    def factory(title='CV', is_default=False, owner=None):
        from django.core.files.base import ContentFile

        content = pdf_bytes(f'{title} - Python, Django ({uuid.uuid4().hex})')
        return cv_services.upload_cv(
            candidate=owner or candidate, file=ContentFile(content, name=f'{title}.pdf'),
            mime_type=CVMimeType.PDF, title=title, is_default=is_default,
        )

    return factory


# ---------------------------------------------------------------- nộp hồ sơ
def test_apply_with_selected_cv(candidate_client, candidate, make_cv, make_job, employer_client):
    make_cv('CV mặc định')
    chosen = make_cv('CV Backend')
    job = make_job(title='Backend Developer')

    res = candidate_client.post(
        APPS, {'job_id': str(job.id), 'cv_id': str(chosen.id), 'cover_letter': '  Em xin ứng tuyển  '}, format='json'
    )

    assert res.status_code == 201, res.data
    assert res.data['status'] == 'applied'
    assert res.data['cv']['title'] == 'CV Backend'
    assert res.data['job']['title'] == 'Backend Developer'
    assert res.data['job']['company']['name'] == 'ACME'
    assert res.data['cover_letter'] == 'Em xin ứng tuyển'
    assert res.data['can_withdraw'] is True
    assert [(h['from_status'], h['to_status']) for h in res.data['status_history']] == [(None, 'applied')]
    job.refresh_from_db()
    assert job.application_count == 1

    # Nhà tuyển dụng thấy hồ sơ mới cùng đúng CV ứng viên chọn
    employer_item = employer_client.get('/api/v1/employer/applications/').data['results'][0]
    assert employer_item['candidate']['id'] == str(candidate.id)
    assert employer_item['cv']['id'] == str(chosen.id)


def test_apply_uses_default_cv_when_cv_not_given(candidate_client, make_cv, make_job):
    make_cv('CV cũ')
    default = make_cv('CV mặc định', is_default=True)

    res = candidate_client.post(APPS, {'job_id': str(make_job().id)}, format='json')

    assert res.status_code == 201
    assert res.data['cv']['id'] == str(default.id)


def test_apply_without_any_cv(candidate_client, make_job):
    res = candidate_client.post(APPS, {'job_id': str(make_job().id)}, format='json')

    assert res.status_code == 400
    assert res.data['errors']['cv_id'] == ['Bạn chưa có CV. Vui lòng tải lên CV trước khi ứng tuyển.']


def test_cannot_apply_with_another_candidates_cv(candidate_client, make_cv, make_job, make_candidate):
    make_cv()
    _, other_cv = make_candidate()

    res = candidate_client.post(APPS, {'job_id': str(make_job().id), 'cv_id': str(other_cv.id)}, format='json')

    assert res.status_code == 400
    assert res.data['errors']['cv_id'] == ['CV không tồn tại.']


def test_cannot_apply_with_deleted_cv(candidate_client, make_cv, make_job):
    cv = make_cv()
    cv_services.delete_cv(cv)

    res = candidate_client.post(APPS, {'job_id': str(make_job().id), 'cv_id': str(cv.id)}, format='json')

    assert res.status_code == 400
    assert 'cv_id' in res.data['errors']


@pytest.mark.parametrize('job_id', ['khong-phai-uuid', str(uuid.uuid4())])
def test_apply_to_unknown_job(candidate_client, make_cv, job_id):
    make_cv()

    res = candidate_client.post(APPS, {'job_id': job_id}, format='json')

    assert res.status_code == 400
    assert 'job_id' in res.data['errors']


def test_draft_job_looks_like_it_does_not_exist(candidate_client, make_cv, make_job):
    make_cv()

    res = candidate_client.post(APPS, {'job_id': str(make_job(publish=False).id)}, format='json')

    assert res.status_code == 400
    assert res.data['errors']['job_id'] == ['Tin tuyển dụng không tồn tại.']


def test_cannot_apply_to_closed_job(candidate_client, make_cv, make_job):
    make_cv()
    job = make_job()
    job_services.close_job(job, by=None)

    res = candidate_client.post(APPS, {'job_id': str(job.id)}, format='json')

    assert res.status_code == 400
    assert res.data['code'] == 'job_not_accepting'


def test_cannot_apply_twice(candidate_client, make_cv, make_job):
    make_cv()
    job = make_job()
    candidate_client.post(APPS, {'job_id': str(job.id)}, format='json')

    res = candidate_client.post(APPS, {'job_id': str(job.id)}, format='json')

    assert res.status_code == 409
    assert res.data['code'] == 'duplicate_application'
    assert Application.objects.count() == 1


def test_cv_not_parsed_yet_can_still_be_submitted(candidate_client, make_cv, make_job):
    cv = make_cv()  # không chạy callback sau commit -> CV vẫn ở trạng thái pending
    assert cv.parse_status == 'pending'

    assert candidate_client.post(APPS, {'job_id': str(make_job().id)}, format='json').status_code == 201


# ---------------------------------------------------------------- theo dõi hồ sơ
def test_list_is_scoped_filtered_and_hides_employer_data(
    candidate_client, candidate, make_cv, make_job, make_application, recruiter
):
    cv = make_cv()
    applied = services.submit_application(candidate=candidate, job=make_job(title='Python Developer'), cv=cv)
    rejected = services.submit_application(candidate=candidate, job=make_job(title='Java Developer'), cv=cv)
    services.change_status(rejected, to_status='screening', by=recruiter.user, note='Ghi chú nội bộ')
    services.change_status(rejected, to_status='rejected', by=recruiter.user, rejection_reason='Lý do nội bộ')
    services.rate_application(rejected, rating=2)
    make_application(make_job(title='Tin của người khác'))  # hồ sơ của ứng viên khác

    def titles(query=''):
        return sorted(a['job']['title'] for a in candidate_client.get(APPS + query).data['results'])

    assert titles() == ['Java Developer', 'Python Developer']
    assert titles('?status=rejected') == ['Java Developer']
    assert titles('?status=applied,screening') == ['Python Developer']
    assert titles('?q=acme') == ['Java Developer', 'Python Developer']  # theo tên công ty
    assert titles('?q=java') == ['Java Developer']

    detail = candidate_client.get(url(rejected.id)).data
    assert detail['status'] == 'rejected' and detail['can_withdraw'] is False
    assert [h['to_status'] for h in detail['status_history']] == ['applied', 'screening', 'rejected']
    flat = str(detail)
    assert 'Ghi chú nội bộ' not in flat and 'Lý do nội bộ' not in flat
    assert not {'recruiter_rating', 'rejection_reason'} & detail.keys()
    assert candidate_client.get(url(applied.id)).data['can_withdraw'] is True


def test_cannot_see_other_candidates_application(candidate_client, make_job, make_application):
    other = make_application(make_job())

    assert candidate_client.get(url(other.id)).status_code == 404
    assert candidate_client.post(url(other.id, 'withdraw')).status_code == 404


def test_closed_job_application_still_listed(candidate_client, candidate, make_cv, make_job):
    job = make_job()
    services.submit_application(candidate=candidate, job=job, cv=make_cv())
    job_services.close_job(job, by=None)

    item = candidate_client.get(APPS).data['results'][0]

    assert item['job']['status'] == 'closed'


# ---------------------------------------------------------------- rút hồ sơ
def test_withdraw_application(candidate_client, candidate, make_cv, make_job, employer_client):
    application = services.submit_application(candidate=candidate, job=make_job(), cv=make_cv())

    res = candidate_client.post(url(application.id, 'withdraw'), {'reason': 'Đã nhận việc nơi khác'}, format='json')

    assert res.status_code == 200
    assert (res.data['status'], res.data['can_withdraw']) == ('withdrawn', False)
    # NTD thấy hồ sơ đã rút, lý do rút trong lịch sử, và không còn thao tác pipeline nào
    employer_view = employer_client.get(f'/api/v1/employer/applications/{application.id}/').data
    assert employer_view['status'] == 'withdrawn'
    assert employer_view['allowed_transitions'] == []
    last = employer_view['status_history'][-1]
    assert (last['to_status'], last['note'], last['changed_by']['id']) == (
        'withdrawn', 'Đã nhận việc nơi khác', str(candidate.user.id),
    )


@pytest.mark.parametrize('statuses', [['screening', 'interview', 'offer', 'hired'], ['rejected']])
def test_cannot_withdraw_finished_application(candidate_client, candidate, make_cv, make_job, recruiter, statuses):
    application = services.submit_application(candidate=candidate, job=make_job(), cv=make_cv())
    for status in statuses:
        application = services.change_status(application, to_status=status, by=recruiter.user)

    res = candidate_client.post(url(application.id, 'withdraw'))

    assert res.status_code == 409
    assert res.data['code'] == 'invalid_status_transition'


def test_withdraw_twice(candidate_client, candidate, make_cv, make_job):
    application = services.submit_application(candidate=candidate, job=make_job(), cv=make_cv())
    candidate_client.post(url(application.id, 'withdraw'))

    assert candidate_client.post(url(application.id, 'withdraw')).status_code == 409


def test_withdraw_sends_status_changed_event(candidate, make_cv, make_job, django_capture_on_commit_callbacks):
    received = []

    def on_changed(sender, application, from_status, to_status, changed_by, **kwargs):
        received.append((from_status, to_status, changed_by))

    signals.application_status_changed.connect(on_changed)
    try:
        application = services.submit_application(candidate=candidate, job=make_job(), cv=make_cv())
        with django_capture_on_commit_callbacks(execute=True):
            services.withdraw_application(application, by=candidate.user)
    finally:
        signals.application_status_changed.disconnect(on_changed)

    assert received == [('applied', 'withdrawn', candidate.user)]


def test_employer_cannot_use_candidate_application_api(employer_client):
    assert employer_client.get(APPS).status_code == 403


def test_end_to_end_register_upload_apply(api_client, make_job, django_capture_on_commit_callbacks):
    """Luồng đầy đủ như frontend: đăng ký -> tải CV -> ứng tuyển -> theo dõi."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    from conftest import PASSWORD

    job = make_job(title='Frontend Developer')
    session = api_client.post(
        '/api/v1/candidate/register/',
        {'full_name': 'Phạm Minh Đức', 'email': 'duc@test.com', 'password': PASSWORD}, format='json',
    ).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {session['access']}")

    with django_capture_on_commit_callbacks(execute=True):
        cv = api_client.post(
            '/api/v1/candidate/cvs/',
            {'file': SimpleUploadedFile('PhamMinhDuc_CV.pdf', pdf_bytes('Pham Minh Duc - React, TypeScript'))},
            format='multipart',
        ).data
    assert api_client.get(f"/api/v1/candidate/cvs/{cv['id']}/").data['parse_status'] == 'completed'

    applied = api_client.post(APPS, {'job_id': str(job.id)}, format='json')
    assert applied.status_code == 201
    assert api_client.get(APPS).data['count'] == 1
    assert api_client.get('/api/v1/auth/me/').data['profile']['cv_count'] == 1
    assert client_for(job.created_by).get('/api/v1/employer/applications/').data['count'] == 1
