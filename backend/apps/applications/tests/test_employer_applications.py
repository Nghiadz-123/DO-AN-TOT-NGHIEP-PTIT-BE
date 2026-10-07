import pytest

from apps.applications import services, signals
from apps.applications.models import Application, ApplicationStatusHistory
from apps.jobs import services as job_services
from common.exceptions import BusinessError

pytestmark = pytest.mark.django_db

APPS = '/api/v1/employer/applications/'


def url(application, action=None):
    return f'{APPS}{application.id}/' + (f'{action}/' if action else '')


# ---------------------------------------------------------------- danh sách & chi tiết
def test_list_is_scoped_to_company(employer_client, make_job, make_application, other_recruiter):
    own = make_application(make_job())
    other_job = make_job(company=other_recruiter.company, created_by=other_recruiter.user)
    foreign = make_application(other_job)

    res = employer_client.get(APPS)

    assert res.status_code == 200
    assert [a['id'] for a in res.data['results']] == [str(own.id)]
    assert employer_client.get(url(foreign)).status_code == 404
    assert employer_client.post(url(foreign, 'status'), {'status': 'screening'}, format='json').status_code == 404


def test_list_filters(employer_client, make_job, make_application):
    job_a, job_b = make_job(title='A'), make_job(title='B')
    make_application(job_a, full_name='Nguyễn Văn An')
    make_application(job_a, full_name='Lê Thị Cúc', statuses=['screening'])
    make_application(job_b, full_name='Phạm Minh Đức', statuses=['rejected'])

    def names(query):
        return sorted(a['candidate']['full_name'] for a in employer_client.get(APPS + query).data['results'])

    assert names(f'?job={job_a.id}') == ['Lê Thị Cúc', 'Nguyễn Văn An']
    assert names('?status=applied,screening') == ['Lê Thị Cúc', 'Nguyễn Văn An']
    assert names('?status=rejected') == ['Phạm Minh Đức']
    assert names('?q=cúc') == ['Lê Thị Cúc']
    assert employer_client.get(APPS + '?status=unknown').status_code == 400


def test_list_ordering_by_applied_at(employer_client, make_job, make_application):
    job = make_job()
    first = make_application(job, full_name='Nộp trước')
    second = make_application(job, full_name='Nộp sau')
    Application.objects.filter(pk=first.pk).update(created_at=second.created_at.replace(year=2025))

    def ids(query):
        return [a['id'] for a in employer_client.get(APPS + query).data['results']]

    assert ids('') == [str(second.id), str(first.id)]  # mặc định: mới nộp nhất
    assert ids('?ordering=applied_at') == [str(first.id), str(second.id)]
    assert ids('?ordering=-applied_at') == [str(second.id), str(first.id)]


def test_list_item_shape(employer_client, make_job, make_application):
    make_application(make_job(title='Python Developer'), full_name='Nguyễn Văn An')

    item = employer_client.get(APPS).data['results'][0]

    assert item['job']['title'] == 'Python Developer'
    assert item['candidate']['full_name'] == 'Nguyễn Văn An'
    assert item['cv']['original_filename'] == 'CV Nguyễn Văn An.pdf'
    assert item['status'] == 'applied'
    assert item['allowed_transitions'] == ['screening', 'interview', 'rejected']
    assert item['applied_at']


def test_detail_includes_history_cover_letter_and_cv_url(employer_client, make_job, make_application):
    application = make_application(make_job(), statuses=['screening'])

    res = employer_client.get(url(application))

    assert res.status_code == 200
    assert [(h['from_status'], h['to_status']) for h in res.data['status_history']] == [
        (None, 'applied'), ('applied', 'screening'),
    ]
    assert res.data['cv_download_url'].endswith(f'/api/v1/employer/applications/{application.id}/cv/')
    assert {'summary', 'cover_letter', 'rejection_reason'} <= set(res.data['candidate']) | set(res.data)


# ---------------------------------------------------------------- pipeline
def test_move_through_pipeline_records_history(employer_client, make_job, make_application, recruiter):
    application = make_application(make_job())

    for status in ['screening', 'interview', 'offer', 'hired']:
        res = employer_client.post(url(application, 'status'), {'status': status, 'note': f'-> {status}'}, format='json')
        assert res.status_code == 200, res.data
        assert res.data['status'] == status

    assert res.data['allowed_transitions'] == []
    last = res.data['status_history'][-1]
    assert (last['from_status'], last['to_status'], last['note']) == ('offer', 'hired', '-> hired')
    assert last['changed_by']['id'] == str(recruiter.user.id)


def test_invite_to_interview_directly_from_applied(employer_client, make_job, make_application):
    application = make_application(make_job())

    res = employer_client.post(url(application, 'status'), {'status': 'interview'}, format='json')

    assert res.status_code == 200


@pytest.mark.parametrize(
    'statuses, target',
    [([], 'offer'), ([], 'hired'), (['screening'], 'screening'), (['screening', 'interview', 'offer', 'hired'], 'rejected')],
)
def test_invalid_transitions(employer_client, make_job, make_application, statuses, target):
    application = make_application(make_job(), statuses=statuses)

    res = employer_client.post(url(application, 'status'), {'status': target}, format='json')

    assert res.status_code == 409
    assert res.data['code'] == 'invalid_status_transition'


@pytest.mark.parametrize('target', ['applied', 'withdrawn'])
def test_employer_cannot_set_candidate_only_statuses(employer_client, make_job, make_application, target):
    application = make_application(make_job())

    res = employer_client.post(url(application, 'status'), {'status': target}, format='json')

    assert res.status_code == 400


def test_reject_with_reason_then_reopen(employer_client, make_job, make_application):
    application = make_application(make_job())

    rejected = employer_client.post(
        url(application, 'status'), {'status': 'rejected', 'rejection_reason': 'Thiếu kinh nghiệm'}, format='json'
    ).data
    assert (rejected['status'], rejected['rejection_reason']) == ('rejected', 'Thiếu kinh nghiệm')
    assert rejected['allowed_transitions'] == ['screening']

    reopened = employer_client.post(url(application, 'status'), {'status': 'screening'}, format='json').data
    assert (reopened['status'], reopened['rejection_reason']) == ('screening', '')


def test_closed_job_applications_can_still_be_processed(employer_client, make_job, make_application):
    job = make_job()
    application = make_application(job)
    job_services.close_job(job, by=None)

    assert employer_client.post(url(application, 'status'), {'status': 'screening'}, format='json').status_code == 200


# ---------------------------------------------------------------- đánh giá & CV
def test_rate_application(employer_client, make_job, make_application):
    application = make_application(make_job())

    assert employer_client.patch(url(application), {'recruiter_rating': 4}, format='json').data['recruiter_rating'] == 4
    assert employer_client.patch(url(application), {'recruiter_rating': 6}, format='json').status_code == 400
    assert employer_client.patch(url(application), {'recruiter_rating': None}, format='json').data['recruiter_rating'] is None


def test_download_cv(employer_client, make_job, make_application):
    application = make_application(make_job(), full_name='Nguyễn Văn An')

    inline = employer_client.get(url(application, 'cv'))
    attachment = employer_client.get(url(application, 'cv') + '?download=1')

    assert inline.status_code == 200
    assert inline['Content-Type'] == 'application/pdf'
    assert inline['Content-Disposition'].startswith('inline')
    assert b''.join(inline.streaming_content) == b'%PDF-1.4 test cv'
    assert attachment['Content-Disposition'].startswith('attachment')
    assert "filename*=utf-8''CV%20Nguy%E1%BB%85n" in attachment['Content-Disposition']


def test_cv_file_missing_returns_404(employer_client, make_job, make_application):
    application = make_application(make_job())
    application.cv.file.delete(save=False)

    res = employer_client.get(url(application, 'cv'))

    assert res.status_code == 404


# ---------------------------------------------------------------- dashboard
def test_dashboard(employer_client, make_job, make_application):
    job = make_job()
    make_job(publish=False)
    make_application(job)
    make_application(job, statuses=['screening'])
    make_application(job, statuses=['rejected'])

    res = employer_client.get('/api/v1/employer/dashboard/')

    assert res.status_code == 200
    assert res.data['jobs'] == {'total': 2, 'draft': 1, 'published': 1, 'paused': 0, 'closed': 0, 'expired': 0}
    stats = res.data['applications']
    assert (stats['total'], stats['applied'], stats['screening'], stats['rejected'], stats['new_last_7_days']) == (3, 1, 1, 1, 3)
    assert len(res.data['recent_applications']) == 3


# ---------------------------------------------------------------- service nộp hồ sơ (API ứng viên dùng ở giai đoạn sau)
def test_submit_application_rules(make_job, make_candidate):
    job = make_job()
    profile, cv = make_candidate()

    application = services.submit_application(candidate=profile, job=job, cv=cv, cover_letter='  Xin chào  ')
    job.refresh_from_db()
    assert application.cover_letter == 'Xin chào'
    assert job.application_count == 1
    assert ApplicationStatusHistory.objects.filter(application=application, to_status='applied').exists()

    with pytest.raises(BusinessError, match='đã ứng tuyển'):
        services.submit_application(candidate=profile, job=job, cv=cv)

    _, other_cv = make_candidate()
    with pytest.raises(BusinessError, match='CV không hợp lệ'):
        services.submit_application(candidate=profile, job=make_job(), cv=other_cv)

    draft = make_job(publish=False)
    with pytest.raises(BusinessError, match='không còn nhận hồ sơ'):
        services.submit_application(candidate=profile, job=draft, cv=cv)
    assert Application.objects.count() == 1


def test_application_events_are_sent(make_job, make_candidate, recruiter, django_capture_on_commit_callbacks):
    received = []

    def on_submitted(sender, application, **kwargs):
        received.append(('submitted', application.status))

    def on_changed(sender, application, from_status, to_status, **kwargs):
        received.append(('changed', from_status, to_status))

    signals.application_submitted.connect(on_submitted)
    signals.application_status_changed.connect(on_changed)
    try:
        profile, cv = make_candidate()
        with django_capture_on_commit_callbacks(execute=True):
            application = services.submit_application(candidate=profile, job=make_job(), cv=cv)
        with django_capture_on_commit_callbacks(execute=True):
            services.change_status(application, to_status='screening', by=recruiter.user)
    finally:
        signals.application_submitted.disconnect(on_submitted)
        signals.application_status_changed.disconnect(on_changed)

    assert received == [('submitted', 'applied'), ('changed', 'applied', 'screening')]
