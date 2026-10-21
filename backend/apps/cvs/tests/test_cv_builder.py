import pytest

from apps.applications import services as application_services
from apps.cvs.models import CV

pytestmark = pytest.mark.django_db

BUILDER = '/api/v1/candidate/cv-builder/'
CVS = '/api/v1/candidate/cvs/'


def content(**overrides):
    data = {
        'fullName': 'Nguyễn Văn An',
        'title': 'Backend Developer',
        'email': 'an.nguyen@example.com',
        'phone': '0912 345 678',
        'location': 'Hà Nội',
        'website': 'github.com/annguyen',
        'summary': 'Lập trình viên backend 3 năm kinh nghiệm với Python và Django.',
        'skills': 'Python, Django, PostgreSQL',
        'experiences': [
            {'role': 'Backend Developer', 'company': 'ACME', 'period': '2022 – nay', 'description': 'Xây API\nTối ưu truy vấn'}
        ],
        'educations': [{'degree': 'Cử nhân CNTT', 'school': 'PTIT', 'period': '2018 – 2022', 'description': ''}],
        'projects': 'Smart ATS — hệ thống tuyển dụng',
    }
    data.update(overrides)
    return data


@pytest.fixture
def save(candidate_client, django_capture_on_commit_callbacks):
    """PUT như frontend rồi chạy các callback sau commit (bóc tách CV).

    Ngoài test, callback chạy ngay khi service commit (trước khi trả response); ở đây chúng chạy sau khi response đã
    dựng nên đọc lại `cv` để có trạng thái bóc tách mới nhất."""

    def do(body):
        with django_capture_on_commit_callbacks(execute=True):
            res = candidate_client.put(BUILDER, {'content': body}, format='json')
        if res.status_code == 200:
            res.data['cv'] = candidate_client.get(BUILDER).data['cv']
        return res

    return do


def test_get_before_saving_returns_empty(candidate_client):
    res = candidate_client.get(BUILDER)
    assert res.status_code == 200
    assert res.data == {'content': None, 'updated_at': None, 'cv': None}


def test_save_creates_real_cv_that_is_parsed(save, candidate_client):
    res = save(content())

    assert res.status_code == 200, res.data
    cv = res.data['cv']
    assert cv['title'] == 'Nguyễn Văn An - Backend Developer'
    assert cv['mime_type'].endswith('wordprocessingml.document')
    assert cv['parse_status'] == 'completed'
    assert cv['is_default'] is True  # CV đầu tiên của ứng viên

    detail = candidate_client.get(f'{CVS}{cv["id"]}/').data
    for text in ('Nguyễn Văn An', 'Backend Developer', 'GIỚI THIỆU', 'KINH NGHIỆM LÀM VIỆC', 'ACME', 'Tối ưu truy vấn',
                 'HỌC VẤN', 'PTIT', 'Python, Django, PostgreSQL', 'Smart ATS'):
        assert text in detail['raw_text'], text
    assert detail['parsed_data']['contact']['emails'] == ['an.nguyen@example.com']
    assert detail['parsed_data']['contact']['phones'] == ['0912345678']
    assert [c['id'] for c in candidate_client.get(CVS).data] == [cv['id']]  # có trong "CV của tôi"
    assert candidate_client.get(f'{CVS}{cv["id"]}/file/').status_code == 200


def test_get_returns_saved_content_and_cv(save, candidate_client):
    cv_id = save(content()).data['cv']['id']

    res = candidate_client.get(BUILDER)

    assert res.data['content']['fullName'] == 'Nguyễn Văn An'
    assert res.data['cv']['id'] == cv_id


def test_resaving_unchanged_content_keeps_cv(save):
    first = save(content()).data['cv']
    second = save(content()).data['cv']

    assert second['id'] == first['id']
    assert second['parsed_at'] == first['parsed_at']  # không bóc tách lại
    assert CV.objects.count() == 1


def test_editing_updates_same_cv_in_place_and_drops_stale_state(save, candidate_client):
    first = save(content()).data['cv']

    second = save(content(summary='Chuyển sang Data Engineer, thành thạo Spark và Airflow.')).data['cv']

    assert second['id'] == first['id']
    assert CV.objects.count() == 1
    assert second['parse_status'] == 'completed'
    assert 'Spark' in candidate_client.get(f'{CVS}{first["id"]}/').data['raw_text']


def test_editing_cv_already_used_for_application_creates_new_cv(save, candidate, make_job):
    first = save(content()).data['cv']
    application_services.submit_application(candidate=candidate, job=make_job(), cv=CV.objects.get(pk=first['id']))

    second = save(content(title='Senior Backend Developer')).data['cv']

    assert second['id'] != first['id']  # bản đã nộp giữ nguyên cho nhà tuyển dụng
    assert CV.objects.count() == 2
    assert 'Senior' not in CV.objects.get(pk=first['id']).raw_text
    assert 'Senior' in CV.objects.get(pk=second['id']).raw_text


def test_cannot_save_empty_cv(save):
    res = save({'fullName': '', 'summary': '', 'skills': '', 'experiences': [{'role': ''}], 'educations': []})

    assert res.status_code == 400
    assert CV.objects.count() == 0


def test_tolerates_malformed_content(save):
    res = save({'fullName': 'An', 'skills': ['Python'], 'experiences': 'x', 'educations': [None, 5], 'summary': {'a': 1}})

    assert res.status_code == 400  # không có mục nội dung hợp lệ nào, không lỗi 500


def test_deleted_cv_is_rebuilt_on_next_save(save, candidate_client, django_capture_on_commit_callbacks):
    first = save(content()).data['cv']
    with django_capture_on_commit_callbacks(execute=True):
        assert candidate_client.delete(f'{CVS}{first["id"]}/').status_code == 204

    assert candidate_client.get(BUILDER).data['cv'] is None
    second = save(content()).data['cv']

    assert second['id'] != first['id']
    assert second['parse_status'] == 'completed'
