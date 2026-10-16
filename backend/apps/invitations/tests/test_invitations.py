import pytest

from apps.applications import services as application_services
from apps.cvs.models import CV
from apps.invitations import services
from apps.invitations.models import Invitation
from apps.jobs import services as job_services
from conftest import client_for

pytestmark = pytest.mark.django_db

EMPLOYER_URL = '/api/v1/employer/invitations/'
CANDIDATE_URL = '/api/v1/candidate/invitations/'


@pytest.fixture
def job(make_job):
    return make_job(title='Nhân viên kinh doanh', skills=('Bán hàng',))


@pytest.fixture
def talent(make_talent):
    profile, _ = make_talent('ban hang', full_name='Nguyễn Văn An')
    return profile


def invite(client, candidate, job, message='Mời bạn ứng tuyển vị trí này.'):
    payload = {'candidate_id': str(candidate.id), 'job_id': str(job.id), 'message': message}
    return client.post(EMPLOYER_URL, payload, format='json')


def test_recruiter_sends_invitation_and_candidate_reads_it(employer_client, recruiter, job, talent):
    res = invite(employer_client, talent, job)

    assert res.status_code == 201
    assert res.data['status'] == 'pending' and res.data['read_at'] is None and res.data['application_id'] is None
    assert res.data['job'] == {'id': str(job.id), 'title': 'Nhân viên kinh doanh', 'status': 'published'}
    assert res.data['candidate']['full_name'] == 'Nguyễn Văn An' and 'email' not in res.data['candidate']
    assert res.data['sender'] == {'full_name': recruiter.user.full_name, 'position': recruiter.position}

    candidate = client_for(talent.user)
    assert candidate.get(f'{CANDIDATE_URL}summary/').data == {'unread': 1}
    listed = candidate.get(CANDIDATE_URL).data['results']
    assert [item['id'] for item in listed] == [res.data['id']]
    assert listed[0]['job']['company']['name'] == 'ACME'
    assert listed[0]['message'] == 'Mời bạn ứng tuyển vị trí này.'

    read = candidate.post(f'{CANDIDATE_URL}{res.data["id"]}/read/')

    assert read.status_code == 200 and read.data['read_at']
    assert candidate.get(f'{CANDIDATE_URL}summary/').data == {'unread': 0}
    assert employer_client.get(EMPLOYER_URL).data['results'][0]['read_at'] == read.data['read_at']


def test_message_is_required(employer_client, job, talent):
    res = invite(employer_client, talent, job, message='   ')

    assert res.status_code == 400 and 'message' in res.data['errors']


def test_only_discoverable_candidates_can_be_invited(employer_client, job, make_job, make_talent, other_recruiter):
    private, _ = make_talent('ban hang', is_public=False)
    res = invite(employer_client, private, job)
    assert res.status_code == 404 and res.data['code'] == 'candidate_not_found'

    # Ứng viên không công khai CV nhưng đã ứng tuyển vào công ty thì mời được cho tin khác
    applicant, cv = make_talent('ban hang', is_public=False)
    application_services.submit_application(candidate=applicant, job=make_job(title='Thủ kho'), cv=cv)
    assert invite(employer_client, applicant, job).status_code == 201

    # Công ty khác không thấy ứng viên chỉ ứng tuyển vào ACME
    other_job = make_job(company=other_recruiter.company, created_by=other_recruiter.user)
    assert invite(client_for(other_recruiter.user), applicant, other_job).status_code == 404


def test_job_must_belong_to_company_and_accept_applications(employer_client, recruiter, talent, make_job,
                                                            other_recruiter):
    foreign = make_job(company=other_recruiter.company, created_by=other_recruiter.user)
    res = invite(employer_client, talent, foreign)
    assert res.status_code == 404 and res.data['code'] == 'job_not_found'

    draft = make_job(publish=False)
    res = invite(employer_client, talent, draft)
    assert res.status_code == 400 and res.data['code'] == 'job_not_accepting'

    closed = make_job()
    job_services.close_job(closed, by=recruiter.user)
    assert invite(employer_client, talent, closed).data['code'] == 'job_not_accepting'


def test_cannot_invite_twice_or_after_applying(employer_client, job, talent, make_talent):
    assert invite(employer_client, talent, job).status_code == 201
    res = invite(employer_client, talent, job)
    assert res.status_code == 409 and res.data['code'] == 'already_invited'

    applicant, cv = make_talent('ban hang')
    application_services.submit_application(candidate=applicant, job=job, cv=cv)
    res = invite(employer_client, applicant, job)
    assert res.status_code == 409 and res.data['code'] == 'already_applied'


def test_candidate_declines_invitation(employer_client, job, talent):
    invitation_id = invite(employer_client, talent, job).data['id']
    candidate = client_for(talent.user)

    res = candidate.post(f'{CANDIDATE_URL}{invitation_id}/decline/')

    assert res.status_code == 200
    assert res.data['status'] == 'declined' and res.data['read_at'] and res.data['responded_at']
    again = candidate.post(f'{CANDIDATE_URL}{invitation_id}/decline/')
    assert again.status_code == 409 and again.data['code'] == 'invalid_invitation_action'
    assert employer_client.get(f'{EMPLOYER_URL}?status=declined').data['count'] == 1
    # Thư đã được phản hồi thì không thu hồi được
    assert employer_client.delete(f'{EMPLOYER_URL}{invitation_id}/').status_code == 409


def test_applying_to_invited_job_marks_invitation_accepted(employer_client, job, talent,
                                                           django_capture_on_commit_callbacks):
    invitation_id = invite(employer_client, talent, job).data['id']
    candidate = client_for(talent.user)
    cv = CV.objects.get(candidate=talent)

    with django_capture_on_commit_callbacks(execute=True):
        res = candidate.post('/api/v1/candidate/applications/', {'job_id': str(job.id), 'cv_id': str(cv.id)},
                             format='json')

    assert res.status_code == 201
    item = candidate.get(f'{CANDIDATE_URL}{invitation_id}/').data
    assert item['status'] == 'accepted' and item['application_id'] == res.data['id'] and item['responded_at']
    assert employer_client.get(EMPLOYER_URL).data['results'][0]['application_id'] == res.data['id']


def test_declined_invitation_becomes_accepted_when_candidate_applies_later(recruiter, job, talent):
    invitation = services.send_invitation(recruiter=recruiter, candidate=talent, job=job, message='Mời')
    services.decline_invitation(invitation)
    application = application_services.submit_application(
        candidate=talent, job=job, cv=CV.objects.get(candidate=talent)
    )

    assert services.mark_applied(application) == 1
    invitation.refresh_from_db()
    assert invitation.status == 'accepted' and invitation.application_id == application.id
    assert services.mark_applied(application) == 0  # gọi lại không đổi gì


def test_any_recruiter_of_company_withdraws_pending_invitation(employer_client, member, job, talent):
    invitation_id = invite(employer_client, talent, job).data['id']
    member_client = client_for(member.user)

    assert member_client.get(EMPLOYER_URL).data['count'] == 1
    assert member_client.delete(f'{EMPLOYER_URL}{invitation_id}/').status_code == 204
    assert not Invitation.objects.exists()
    assert client_for(talent.user).get(f'{CANDIDATE_URL}summary/').data == {'unread': 0}
    assert invite(employer_client, talent, job).status_code == 201  # thu hồi rồi thì mời lại được


def test_invitations_are_private(employer_client, job, talent, other_recruiter, candidate_client):
    invitation_id = invite(employer_client, talent, job).data['id']

    other = client_for(other_recruiter.user)
    assert other.get(EMPLOYER_URL).data['count'] == 0
    assert other.delete(f'{EMPLOYER_URL}{invitation_id}/').status_code == 404
    # Ứng viên khác không xem được thư; mỗi vai trò chỉ dùng API của mình
    assert candidate_client.get(f'{CANDIDATE_URL}{invitation_id}/').status_code == 404
    assert candidate_client.post(f'{CANDIDATE_URL}{invitation_id}/decline/').status_code == 404
    assert candidate_client.get(EMPLOYER_URL).status_code == 403
    assert employer_client.get(CANDIDATE_URL).status_code == 403


def test_employer_filters_sent_invitations(employer_client, recruiter, job, make_job, make_talent):
    an, _ = make_talent('ban hang', full_name='Nguyễn Văn An')
    binh, _ = make_talent('ban hang', full_name='Trần Bình')
    services.send_invitation(recruiter=recruiter, candidate=an, job=job, message='Mời')
    second = services.send_invitation(recruiter=recruiter, candidate=binh, job=make_job(title='Thủ kho'), message='Mời')
    services.decline_invitation(second)

    def names(query=''):
        return [item['candidate']['full_name'] for item in employer_client.get(EMPLOYER_URL + query).data['results']]

    assert names() == ['Trần Bình', 'Nguyễn Văn An']  # mới gửi trước
    assert names(f'?job_id={job.id}') == ['Nguyễn Văn An']
    assert names('?status=declined') == ['Trần Bình']
    assert names('?q=bình') == ['Trần Bình']
    assert employer_client.get(EMPLOYER_URL + '?status=unknown').status_code == 400


def test_invitations_of_deleted_job_are_hidden(employer_client, job, talent):
    invite(employer_client, talent, job)
    job.soft_delete()
    candidate = client_for(talent.user)

    assert candidate.get(CANDIDATE_URL).data['count'] == 0
    assert candidate.get(f'{CANDIDATE_URL}summary/').data == {'unread': 0}
    assert employer_client.get(EMPLOYER_URL).data['count'] == 0
