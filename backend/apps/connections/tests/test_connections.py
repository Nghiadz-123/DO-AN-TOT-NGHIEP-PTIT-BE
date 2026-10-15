from datetime import timedelta

import pytest
from django.utils import timezone

from apps.connections import selectors
from apps.connections.models import Connection, ConnectionStatus
from apps.messaging.models import Conversation
from conftest import client_for

pytestmark = pytest.mark.django_db

CONNECTIONS = '/api/v1/connections/'
REQUESTS = '/api/v1/connections/requests/'


def url(connection, action=None):
    return f'{CONNECTIONS}{connection["id"] if isinstance(connection, dict) else connection.id}/' + (
        f'{action}/' if action else ''
    )


def invite(client, profile, **extra):
    return client.post(CONNECTIONS, {'user_id': str(profile.user_id), **extra}, format='json')


def test_employer_invites_and_candidate_accepts(employer_client, recruiter, make_job, make_talent,
                                                django_capture_on_commit_callbacks):
    job = make_job(title='Nhân viên kinh doanh')
    profile, _ = make_talent('ban hang', full_name='Nguyễn Văn An', headline='Sales')
    candidate = client_for(profile.user)

    res = invite(employer_client, profile, job_id=str(job.id), message='  Chào An, mời bạn trao đổi về vị trí này.  ')

    assert res.status_code == 201, res.data
    assert res.data['status'] == 'pending'
    assert res.data['direction'] == 'sent'
    assert res.data['user']['full_name'] == 'Nguyễn Văn An'
    assert res.data['user']['headline'] == 'Sales'
    assert res.data['user']['candidate_id'] == str(profile.id)
    assert res.data['job'] == {'id': str(job.id), 'title': 'Nhân viên kinh doanh'}
    assert res.data['message'] == 'Chào An, mời bạn trao đổi về vị trí này.'

    received = candidate.get(REQUESTS).data
    assert received['count'] == 1
    request = received['results'][0]
    assert request['direction'] == 'received'
    assert request['user']['company']['name'] == 'ACME'
    assert request['user']['candidate_id'] is None
    assert employer_client.get(REQUESTS).data['count'] == 0  # NTD không có lời mời nào chờ mình phản hồi

    with django_capture_on_commit_callbacks(execute=True):
        accepted = candidate.post(url(request, 'accept'))

    assert accepted.status_code == 200
    assert accepted.data['status'] == 'accepted' and accepted.data['responded_at']
    assert [f['user']['full_name'] for f in employer_client.get(CONNECTIONS).data['results']] == ['Nguyễn Văn An']
    assert [f['user']['id'] for f in candidate.get(CONNECTIONS).data['results']] == [str(recruiter.user_id)]
    assert candidate.get(REQUESTS).data['count'] == 0
    # Chấp nhận lời mời: hội thoại được tạo, lời nhắn kèm lời mời là tin nhắn đầu tiên (đã đọc)
    conversation = Conversation.objects.get()
    message = conversation.messages.get()
    assert message.sender == recruiter.user
    assert message.body == 'Chào An, mời bạn trao đổi về vị trí này.'
    assert message.read_at is not None


def test_cannot_invite_undiscoverable_or_non_candidate(employer_client, make_talent, make_job, other_recruiter):
    private, _ = make_talent('ban hang', is_public=False)
    public, _ = make_talent('ban hang')
    foreign_job = make_job(company=other_recruiter.company, created_by=other_recruiter.user)

    res = invite(employer_client, private)
    assert res.status_code == 404
    assert res.data['code'] == 'candidate_not_found'

    res = employer_client.post(CONNECTIONS, {'user_id': str(other_recruiter.user_id)}, format='json')
    assert res.status_code == 400
    assert res.data['errors']['user_id'] == ['Không tìm thấy ứng viên.']

    res = invite(employer_client, public, job_id=str(foreign_job.id))
    assert res.status_code == 400
    assert 'job_id' in res.data['errors']
    assert Connection.objects.count() == 0


def test_applicant_can_be_invited_even_if_private(employer_client, make_application, make_job):
    application = make_application(make_job())  # hồ sơ ứng viên mặc định không công khai

    res = employer_client.post(CONNECTIONS, {'user_id': str(application.candidate.user_id)}, format='json')

    assert res.status_code == 201


def test_only_employer_can_send_requests(candidate_client, recruiter):
    res = candidate_client.post(CONNECTIONS, {'user_id': str(recruiter.user_id)}, format='json')

    assert res.status_code == 403


def test_duplicate_request_and_resend_cooldown(employer_client, make_talent):
    profile, _ = make_talent('ban hang')
    candidate = client_for(profile.user)
    first = invite(employer_client, profile).data

    duplicate = invite(employer_client, profile)
    assert duplicate.status_code == 409
    assert duplicate.data['code'] == 'request_pending'

    assert candidate.post(url(first, 'decline')).data['status'] == 'declined'
    assert candidate.post(url(first, 'accept')).status_code == 409  # đã phản hồi rồi
    too_soon = invite(employer_client, profile)
    assert too_soon.status_code == 409
    assert too_soon.data['code'] == 'request_declined_recently'
    # Lời mời bị từ chối vẫn nằm trong hộp "đã gửi" để NTD biết
    assert [r['status'] for r in employer_client.get(REQUESTS + '?box=sent').data['results']] == ['declined']

    Connection.objects.update(responded_at=timezone.now() - timedelta(days=8))
    resent = invite(employer_client, profile, message='Mời lại')

    assert resent.status_code == 201
    assert resent.data['id'] == first['id']  # dùng lại bản ghi cũ
    assert resent.data['status'] == 'pending' and resent.data['responded_at'] is None
    assert candidate.get(REQUESTS).data['results'][0]['message'] == 'Mời lại'


def test_only_addressee_can_respond(employer_client, make_talent):
    profile, _ = make_talent('ban hang')
    stranger, _ = make_talent('ban hang')
    connection = invite(employer_client, profile).data

    res = employer_client.post(url(connection, 'accept'))
    assert res.status_code == 403
    assert client_for(stranger.user).post(url(connection, 'accept')).status_code == 404
    assert client_for(stranger.user).delete(url(connection)).status_code == 404


def test_cancel_request_and_unfriend(employer_client, recruiter, make_talent, connect):
    pending_profile, _ = make_talent('ban hang')
    pending = invite(employer_client, pending_profile).data

    assert client_for(pending_profile.user).delete(url(pending)).status_code == 409  # người nhận phải từ chối
    assert employer_client.delete(url(pending)).status_code == 204
    assert not Connection.objects.filter(pk=pending['id']).exists()

    friend, _ = make_talent('ban hang')
    friendship = connect(friend)
    assert selectors.are_connected(recruiter.user, friend.user)

    assert client_for(friend.user).delete(url(friendship)).status_code == 204
    assert not selectors.are_connected(recruiter.user, friend.user)
    assert employer_client.get(CONNECTIONS).data['count'] == 0


def test_declined_request_cannot_be_deleted(employer_client, make_talent):
    profile, _ = make_talent('ban hang')
    connection = invite(employer_client, profile).data
    client_for(profile.user).post(url(connection, 'decline'))

    res = employer_client.delete(url(connection))

    assert res.status_code == 409
    assert Connection.objects.get().status == ConnectionStatus.DECLINED


def test_search_friends_by_name(employer_client, make_talent, connect):
    connect(make_talent('ban hang', full_name='Nguyễn Văn An')[0])
    connect(make_talent('ban hang', full_name='Lê Thị Cúc')[0])

    res = employer_client.get(CONNECTIONS + '?q=cúc')

    assert [f['user']['full_name'] for f in res.data['results']] == ['Lê Thị Cúc']
