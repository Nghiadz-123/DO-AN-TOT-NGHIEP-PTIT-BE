import pytest

from apps.connections import selectors as connection_selectors
from apps.connections import services as connection_services
from apps.messaging import selectors
from apps.messaging.models import Conversation, Message
from conftest import client_for

pytestmark = pytest.mark.django_db

CONVERSATIONS = '/api/v1/conversations/'
SUMMARY = '/api/v1/conversations/summary/'


def messages_url(conversation_id, query=''):
    return f'{CONVERSATIONS}{conversation_id}/messages/{query}'


@pytest.fixture
def friend(make_talent, connect):
    """Ứng viên đã kết bạn với nhà tuyển dụng ACME."""
    profile, _ = make_talent('ban hang', full_name='Nguyễn Văn An', headline='Sales')
    connect(profile)
    return profile


def open_conversation(client, user):
    return client.post(CONVERSATIONS, {'user_id': str(user.pk)}, format='json')


def test_open_conversation_requires_friendship(employer_client, recruiter, make_talent, friend):
    stranger, _ = make_talent('ban hang')

    res = open_conversation(employer_client, stranger.user)
    assert res.status_code == 403
    assert res.data['code'] == 'not_connected'

    created = open_conversation(employer_client, friend.user)
    assert created.status_code == 201
    assert created.data['user']['full_name'] == 'Nguyễn Văn An'
    assert created.data['user']['headline'] == 'Sales'
    assert created.data['can_send'] is True
    assert created.data['last_message'] is None
    # Mở lại từ phía còn lại: cùng một hội thoại
    again = open_conversation(client_for(friend.user), recruiter.user)
    assert again.status_code == 200
    assert again.data['id'] == created.data['id']
    assert again.data['user']['company']['name'] == 'ACME'
    assert Conversation.objects.count() == 1


def test_send_poll_and_read_messages(employer_client, recruiter, friend):
    candidate = client_for(friend.user)
    conversation_id = open_conversation(employer_client, friend.user).data['id']

    first = employer_client.post(messages_url(conversation_id), {'body': '  Chào An!  '}, format='json')
    assert first.status_code == 201, first.data
    assert first.data['body'] == 'Chào An!'
    assert first.data['is_mine'] is True
    second = employer_client.post(messages_url(conversation_id), {'body': 'Bạn rảnh trao đổi chiều nay không?'},
                                  format='json').data

    # Ứng viên: 2 tin chưa đọc
    assert candidate.get(SUMMARY).data == {'unread_messages': 2, 'unread_conversations': 1, 'pending_requests': 0}
    listed = candidate.get(CONVERSATIONS).data['results'][0]
    assert listed['unread_count'] == 2
    assert listed['last_message'] == {'id': second['id'], 'body': second['body'], 'is_mine': False}

    res = candidate.get(messages_url(conversation_id))
    assert [m['body'] for m in res.data['results']] == ['Chào An!', 'Bạn rảnh trao đổi chiều nay không?']
    assert [m['is_mine'] for m in res.data['results']] == [False, False]
    assert res.data['has_more'] is False

    assert candidate.post(f'{CONVERSATIONS}{conversation_id}/read/').status_code == 204
    assert candidate.get(SUMMARY).data['unread_messages'] == 0
    assert employer_client.get(SUMMARY).data['unread_messages'] == 0  # tin mình gửi không tính là chưa đọc

    reply = candidate.post(messages_url(conversation_id), {'body': 'Dạ được ạ'}, format='json').data
    # Hỏi định kỳ: chỉ lấy tin mới hơn tin cuối đã có
    newer = employer_client.get(messages_url(conversation_id, f'?after={second["id"]}')).data
    assert [m['id'] for m in newer['results']] == [reply['id']]
    assert employer_client.get(messages_url(conversation_id, f'?after={reply["id"]}')).data['results'] == []
    older = employer_client.get(messages_url(conversation_id, f'?before={second["id"]}')).data
    assert [m['id'] for m in older['results']] == [first.data['id']]


def test_load_older_messages_in_pages(employer_client, recruiter, friend):
    conversation = Conversation.objects.get(pk=open_conversation(employer_client, friend.user).data['id'])
    Message.objects.bulk_create(
        Message(conversation=conversation, sender=recruiter.user, body=f'Tin {n}')
        for n in range(selectors.MESSAGES_PAGE_SIZE + 5)
    )

    latest = employer_client.get(messages_url(conversation.id)).data
    assert len(latest['results']) == selectors.MESSAGES_PAGE_SIZE
    assert latest['has_more'] is True
    assert latest['results'][-1]['body'] == f'Tin {selectors.MESSAGES_PAGE_SIZE + 4}'

    rest = employer_client.get(messages_url(conversation.id, f'?before={latest["results"][0]["id"]}')).data
    assert [m['body'] for m in rest['results']] == [f'Tin {n}' for n in range(5)]
    assert rest['has_more'] is False


def test_conversation_is_private_to_participants(employer_client, make_talent, friend):
    conversation_id = open_conversation(employer_client, friend.user).data['id']
    outsider = client_for(make_talent('ban hang')[0].user)

    assert outsider.get(f'{CONVERSATIONS}{conversation_id}/').status_code == 404
    assert outsider.get(messages_url(conversation_id)).status_code == 404
    assert outsider.post(messages_url(conversation_id), {'body': 'Xin chào'}, format='json').status_code == 404
    assert outsider.get(CONVERSATIONS).data['count'] == 0


def test_unfriend_keeps_history_but_blocks_sending(employer_client, recruiter, friend):
    conversation_id = open_conversation(employer_client, friend.user).data['id']
    employer_client.post(messages_url(conversation_id), {'body': 'Chào bạn'}, format='json')
    connection = connection_selectors.connection_between(recruiter.user, friend.user)
    connection_services.remove_connection(connection, by=friend.user)

    detail = employer_client.get(f'{CONVERSATIONS}{conversation_id}/')
    assert detail.data['can_send'] is False
    assert len(employer_client.get(messages_url(conversation_id)).data['results']) == 1
    res = employer_client.post(messages_url(conversation_id), {'body': 'Còn đó không?'}, format='json')
    assert res.status_code == 403
    assert res.data['code'] == 'not_connected'


def test_blank_message_is_rejected(employer_client, friend):
    conversation_id = open_conversation(employer_client, friend.user).data['id']

    res = employer_client.post(messages_url(conversation_id), {'body': '   '}, format='json')

    assert res.status_code == 400
    assert 'body' in res.data['errors']


def test_conversations_sorted_by_latest_message(employer_client, make_talent, connect):
    first, _ = make_talent('ban hang', full_name='Người thứ nhất')
    second, _ = make_talent('ban hang', full_name='Người thứ hai')
    for profile in (first, second):
        connect(profile)
    first_id = open_conversation(employer_client, first.user).data['id']
    open_conversation(employer_client, second.user)
    employer_client.post(messages_url(first_id), {'body': 'Tin mới'}, format='json')

    res = employer_client.get(CONVERSATIONS)

    assert [c['user']['full_name'] for c in res.data['results']] == ['Người thứ nhất', 'Người thứ hai']


def test_summary_counts_pending_requests(recruiter, make_talent):
    profile, _ = make_talent('ban hang')
    connection_services.send_request(recruiter=recruiter, addressee=profile.user)

    assert client_for(profile.user).get(SUMMARY).data['pending_requests'] == 1


def test_admin_cannot_use_chat(db):
    from apps.accounts.models import User

    admin = User.objects.create_superuser(email='admin@test.com', password='x')

    assert client_for(admin).get(CONVERSATIONS).status_code == 403
