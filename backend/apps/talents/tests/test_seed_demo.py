import io

import pytest
from django.core.management import call_command

from apps.accounts.models import User
from apps.jobs.models import Job
from apps.messaging.models import Conversation
from conftest import client_for

pytestmark = pytest.mark.django_db


def test_seed_demo_has_suggestions_connections_and_chat(django_capture_on_commit_callbacks):
    # Bóc tách CV và tạo hội thoại chạy sau commit như khi dùng thật
    with django_capture_on_commit_callbacks(execute=True):
        call_command('seed_demo', '--force', stdout=io.StringIO())

    recruiter = client_for(User.objects.get(email='recruiter@demo.com'))
    sales = Job.objects.get(title='Nhân viên kinh doanh khách hàng doanh nghiệp')
    results = recruiter.get(f'/api/v1/employer/jobs/{sales.id}/suggested-candidates/').data['results']

    best = results[0]
    assert best['candidate']['full_name'] == 'Nguyễn Văn An'
    assert best['matched_skills'] == ['Bán hàng', 'Đàm phán', 'Chăm sóc khách hàng', 'Tin học văn phòng']
    assert best['connection']['status'] == 'accepted'
    # Đỗ Mai Linh không công khai hồ sơ nhưng đã ứng tuyển vào Sao Việt nên vẫn được gợi ý
    linh = next(r for r in results if r['candidate']['full_name'] == 'Đỗ Mai Linh')
    assert linh['application_id']

    conversation = Conversation.objects.get()
    assert conversation.messages.count() == 4  # lời nhắn kèm lời mời + 3 tin nhắn
    cuc = client_for(User.objects.get(email='cuc.le@demo.com'))
    assert cuc.get('/api/v1/conversations/summary/').data['pending_requests'] == 1
