import io

import pytest
from django.core.management import call_command

from apps.accounts.models import User
from apps.jobs.models import Job
from conftest import client_for

pytestmark = pytest.mark.django_db


def test_seed_demo_has_talents_and_invitations(django_capture_on_commit_callbacks):
    # Bóc tách CV và các event sau khi nộp hồ sơ chạy sau commit như khi dùng thật
    with django_capture_on_commit_callbacks(execute=True):
        call_command('seed_demo', '--force', stdout=io.StringIO())

    recruiter = client_for(User.objects.get(email='recruiter@demo.com'))
    sales = Job.objects.get(title='Nhân viên kinh doanh khách hàng doanh nghiệp')
    results = recruiter.get(f'/api/v1/employer/jobs/{sales.id}/suggested-candidates/').data['results']

    best = results[0]
    assert best['candidate']['full_name'] == 'Nguyễn Văn An'
    assert best['matched_skills'] == ['Bán hàng', 'Đàm phán', 'Chăm sóc khách hàng', 'Tin học văn phòng']
    # Đỗ Mai Linh không công khai CV nhưng đã ứng tuyển vào Sao Việt nên vẫn được gợi ý
    linh = next(r for r in results if r['candidate']['full_name'] == 'Đỗ Mai Linh')
    assert linh['application_id']
    huy = next(r for r in results if r['candidate']['full_name'] == 'Vũ Quốc Huy')
    assert huy['invitation']['status'] == 'declined'

    # Tìm ứng viên: chỉ ứng viên công khai CV (không có Đỗ Mai Linh)
    pool = recruiter.get('/api/v1/employer/talents/').data
    assert pool['count'] == 5
    assert 'Đỗ Mai Linh' not in [item['candidate']['full_name'] for item in pool['results']]

    sent = recruiter.get('/api/v1/employer/invitations/').data['results']
    assert sorted(item['status'] for item in sent) == ['accepted', 'accepted', 'accepted', 'declined']
    assert all(item['application_id'] for item in sent if item['status'] == 'accepted')

    candidate = client_for(User.objects.get(email='candidate@demo.com'))
    assert candidate.get('/api/v1/candidate/invitations/summary/').data == {'unread': 1}
    received = candidate.get('/api/v1/candidate/invitations/').data['results']
    assert [(item['job']['company']['name'], item['status']) for item in received] == [
        ('Khách sạn Biển Xanh Nha Trang', 'pending'),
        ('Công ty CP Bán lẻ Sao Việt', 'accepted'),
    ]
