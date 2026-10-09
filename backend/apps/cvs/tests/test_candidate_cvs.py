import io
import zipfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from pypdf import PdfReader, PdfWriter

from apps.applications import services as application_services
from apps.cvs import signals
from apps.cvs.models import CV
from conftest import client_for, docx_bytes, pdf_bytes

pytestmark = pytest.mark.django_db

CVS = '/api/v1/candidate/cvs/'
DOCX_MIME = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


def url(cv_id, action=None):
    return f'{CVS}{cv_id}/' + (f'{action}/' if action else '')


@pytest.fixture
def upload(candidate_client, django_capture_on_commit_callbacks):
    """Upload như frontend rồi chạy các callback sau commit (bóc tách CV) như môi trường thật."""

    def do(file, client=None, **data):
        with django_capture_on_commit_callbacks(execute=True):
            return (client or candidate_client).post(CVS, {'file': file, **data}, format='multipart')

    return do


# ---------------------------------------------------------------- upload & bóc tách
def test_upload_pdf_is_parsed(upload, candidate_client, candidate):
    file = SimpleUploadedFile(
        'NguyenVanAn_Backend_CV.pdf',
        pdf_bytes('Nguyen Van An - Backend Developer', 'Email: An.Nguyen@Example.com | DT: 0912 345 678',
                  'Python, Django, PostgreSQL. https://github.com/annguyen'),
        content_type='application/pdf',
    )

    res = upload(file)

    assert res.status_code == 201, res.data
    assert res.data['title'] == 'NguyenVanAn Backend CV'  # mặc định lấy theo tên file
    assert (res.data['original_filename'], res.data['mime_type']) == ('NguyenVanAn_Backend_CV.pdf', 'application/pdf')
    assert res.data['is_default'] is True  # CV đầu tiên là mặc định
    assert res.data['file_url'].endswith(f'/api/v1/candidate/cvs/{res.data["id"]}/file/')

    data = candidate_client.get(url(res.data['id'])).data
    assert data['parse_status'] == 'completed'
    assert data['parsed_at'] is not None
    assert 'Backend Developer' in data['raw_text']
    assert data['parsed_data']['stats']['pages'] == 1
    assert data['parsed_data']['contact'] == {
        'emails': ['an.nguyen@example.com'], 'phones': ['0912345678'], 'links': ['https://github.com/annguyen'],
    }
    cv = CV.objects.get(pk=res.data['id'])
    assert cv.candidate == candidate
    assert cv.file.name.startswith(f'cvs/{candidate.id}/')  # tên lưu trữ ngẫu nhiên, không dùng tên file gốc
    assert len(cv.file_hash) == 64


def test_upload_docx_keeps_vietnamese_and_reads_header(upload, candidate_client):
    file = SimpleUploadedFile(
        'cv.docx',
        docx_bytes('KINH NGHIỆM LÀM VIỆC', 'Lập trình viên Backend tại Công ty Giải pháp Số Việt',
                   header='Lê Thị Cúc — cuc.le@gmail.com — +84 901 111 220'),
        content_type=DOCX_MIME,
    )

    res = upload(file, title='CV tiếng Việt', is_default='true')

    assert res.status_code == 201, res.data
    data = candidate_client.get(url(res.data['id'])).data
    assert data['parse_status'] == 'completed'
    assert data['raw_text'].startswith('Lê Thị Cúc')
    assert 'Lập trình viên Backend' in data['raw_text']
    assert data['language'] == 'vi'
    assert data['parsed_data']['contact']['phones'] == ['+84901111220']


def test_scanned_pdf_fails_with_clear_message_and_can_be_retried(upload, candidate_client):
    res = upload(SimpleUploadedFile('scan.pdf', pdf_bytes(), content_type='application/pdf'))

    assert res.status_code == 201  # file vẫn được lưu, chỉ bóc tách thất bại
    data = candidate_client.get(url(res.data['id'])).data
    assert data['parse_status'] == 'failed'
    assert 'dạng ảnh hoặc bản scan' in data['parse_error']
    assert data['raw_text'] == '' and data['parsed_data'] is None

    retry = candidate_client.post(url(res.data['id'], 'reparse'))
    assert retry.status_code == 200
    assert retry.data['parse_status'] == 'pending'  # đã xếp lịch bóc tách lại


def test_password_protected_pdf_fails(upload, candidate_client):
    writer = PdfWriter(clone_from=PdfReader(io.BytesIO(pdf_bytes('Nguyen Van An - Backend Developer, 3 nam'))))
    writer.encrypt(user_password='bi-mat', owner_password='chu-so-huu', algorithm='RC4-128')
    buffer = io.BytesIO()
    writer.write(buffer)

    res = upload(SimpleUploadedFile('locked.pdf', buffer.getvalue(), content_type='application/pdf'))

    data = candidate_client.get(url(res.data['id'])).data
    assert data['parse_status'] == 'failed'
    assert 'mật khẩu' in data['parse_error']


def test_completed_cv_cannot_be_reparsed(upload, candidate_client, cv_upload):
    cv_id = upload(cv_upload()).data['id']

    res = candidate_client.post(url(cv_id, 'reparse'))

    assert res.status_code == 409
    assert res.data['code'] == 'invalid_parse_status'


# ---------------------------------------------------------------- kiểm tra file
@pytest.mark.parametrize(
    'name, content',
    [
        ('cv.doc', b'\xd0\xcf\x11\xe0 word 97'),                     # Word 97-2003 không hỗ trợ
        ('cv.png', b'\x89PNG\r\n\x1a\n'),                            # ảnh
        ('cv.pdf', b'day khong phai pdf'),                           # đổi đuôi
        ('cv.docx', b'%PDF-1.4 thuc chat la pdf'),                   # đuôi không khớp nội dung
        ('cv.pdf', docx_bytes('Noi dung DOCX nhung dat ten la pdf')),
        ('cv.docx', b'PK\x03\x04 zip hong'),
    ],
    ids=['doc-97', 'image', 'fake-pdf', 'pdf-named-docx', 'docx-named-pdf', 'broken-zip'],
)
def test_rejects_invalid_files(candidate_client, name, content):
    res = candidate_client.post(CVS, {'file': SimpleUploadedFile(name, content)}, format='multipart')

    assert res.status_code == 400
    assert 'file' in res.data['errors']
    assert not CV.objects.exists()


def test_rejects_other_office_zip_as_docx(candidate_client):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('xl/workbook.xml', '<workbook/>')

    res = candidate_client.post(CVS, {'file': SimpleUploadedFile('cv.docx', buffer.getvalue())}, format='multipart')

    assert res.status_code == 400


def test_rejects_docx_with_macro(candidate_client):
    buffer = io.BytesIO(docx_bytes('Noi dung'))
    with zipfile.ZipFile(buffer, 'a') as archive:
        archive.writestr('word/vbaProject.bin', b'macro')

    res = candidate_client.post(CVS, {'file': SimpleUploadedFile('cv.docx', buffer.getvalue())}, format='multipart')

    assert res.status_code == 400
    assert 'macro' in res.data['errors']['file'][0]


def test_rejects_empty_and_missing_file(candidate_client):
    empty = candidate_client.post(CVS, {'file': SimpleUploadedFile('cv.pdf', b'')}, format='multipart')
    missing = candidate_client.post(CVS, {'title': 'Không có file'}, format='multipart')

    assert empty.status_code == 400 and 'file' in empty.data['errors']
    assert missing.status_code == 400 and 'file' in missing.data['errors']


@override_settings(CV_MAX_SIZE=1024)
def test_rejects_file_too_large(candidate_client):
    big = SimpleUploadedFile('cv.pdf', pdf_bytes('x' * 50, *['Dong noi dung'] * 60))
    assert big.size > 1024

    res = candidate_client.post(CVS, {'file': big}, format='multipart')

    assert res.status_code == 400
    assert 'dung lượng' in res.data['errors']['file'][0]


def test_rejects_duplicate_file(candidate_client, upload):
    content = pdf_bytes('Nguyen Van An - CV giong het nhau, Python Django')
    upload(SimpleUploadedFile('a.pdf', content), title='CV gốc')

    res = candidate_client.post(CVS, {'file': SimpleUploadedFile('b.pdf', content)}, format='multipart')

    assert res.status_code == 409
    assert res.data['code'] == 'duplicate_cv'
    assert 'CV gốc' in res.data['detail']


@override_settings(CANDIDATE_MAX_CVS=2)
def test_limit_number_of_cvs(candidate_client, upload, cv_upload):
    upload(cv_upload())
    upload(cv_upload())

    res = candidate_client.post(CVS, {'file': cv_upload()}, format='multipart')

    assert res.status_code == 400
    assert res.data['code'] == 'cv_limit_reached'


# ---------------------------------------------------------------- danh sách / chi tiết / phân quyền
def test_list_only_own_cvs_default_first(candidate_client, upload, cv_upload, make_candidate):
    first = upload(cv_upload(), title='CV 1').data
    second = upload(cv_upload(kind='docx'), title='CV 2').data
    make_candidate()  # ứng viên khác cũng có CV

    res = candidate_client.get(CVS)

    assert res.status_code == 200
    assert [cv['id'] for cv in res.data] == [first['id'], second['id']]  # CV mặc định đứng đầu, không phân trang
    assert res.data[0]['application_count'] == 0
    assert 'raw_text' not in res.data[0]  # danh sách không trả văn bản dài


def test_cannot_access_other_candidate_cv(candidate_client, make_candidate):
    _, other_cv = make_candidate()

    assert candidate_client.get(url(other_cv.id)).status_code == 404
    assert candidate_client.get(url(other_cv.id, 'file')).status_code == 404
    assert candidate_client.patch(url(other_cv.id), {'title': 'x'}, format='json').status_code == 404
    assert candidate_client.delete(url(other_cv.id)).status_code == 404
    assert candidate_client.post(url(other_cv.id, 'set-default')).status_code == 404


def test_employer_cannot_use_cv_api(employer_client):
    assert employer_client.get(CVS).status_code == 403


# ---------------------------------------------------------------- sửa / mặc định / xóa
def test_rename_cv(candidate_client, upload, cv_upload):
    cv_id = upload(cv_upload()).data['id']

    res = candidate_client.patch(url(cv_id), {'title': '  CV Backend   tiếng Anh '}, format='json')
    blank = candidate_client.patch(url(cv_id), {'title': '  '}, format='json')

    assert res.status_code == 200
    assert res.data['title'] == 'CV Backend tiếng Anh'
    assert blank.status_code == 400 and 'title' in blank.data['errors']


def test_switch_default_cv(candidate_client, upload, cv_upload):
    first = upload(cv_upload()).data['id']
    second = upload(cv_upload(), is_default='true').data['id']  # đặt mặc định ngay khi upload
    assert not CV.objects.get(pk=first).is_default

    res = candidate_client.post(url(first, 'set-default'))

    assert res.status_code == 200 and res.data['is_default'] is True
    assert list(CV.objects.filter(is_default=True).values_list('id', flat=True)) == [CV.objects.get(pk=first).id]
    assert not CV.objects.get(pk=second).is_default


def test_delete_unused_cv_removes_file_and_promotes_next_default(
    candidate_client, upload, cv_upload, django_capture_on_commit_callbacks
):
    older = upload(cv_upload()).data['id']
    default = upload(cv_upload(), is_default='true').data['id']
    stored = CV.objects.get(pk=default).file.name
    storage = CV.objects.get(pk=default).file.storage

    with django_capture_on_commit_callbacks(execute=True):
        res = candidate_client.delete(url(default))

    assert res.status_code == 204
    assert candidate_client.get(url(default)).status_code == 404
    assert not storage.exists(stored)  # dữ liệu cá nhân không còn dùng thì xóa file
    deleted = CV.all_objects.get(pk=default)
    assert deleted.deleted_at is not None and deleted.file.name == ''
    assert CV.objects.get(pk=older).is_default  # CV còn lại trở thành mặc định
    assert candidate_client.get('/api/v1/auth/me/').data['profile']['cv_count'] == 1


def test_delete_cv_used_in_application_keeps_file_for_employer(
    candidate_client, candidate, upload, cv_upload, make_job, employer_client, django_capture_on_commit_callbacks
):
    cv_id = upload(cv_upload()).data['id']
    application = application_services.submit_application(
        candidate=candidate, job=make_job(), cv=CV.objects.get(pk=cv_id)
    )
    assert candidate_client.get(CVS).data[0]['application_count'] == 1

    with django_capture_on_commit_callbacks(execute=True):
        assert candidate_client.delete(url(cv_id)).status_code == 204

    assert candidate_client.get(CVS).data == []
    res = employer_client.get(f'/api/v1/employer/applications/{application.id}/cv/')
    assert res.status_code == 200  # NTD vẫn xem được đúng bản CV đã nhận
    assert b''.join(res.streaming_content).startswith(b'%PDF')


def test_deleted_cv_can_be_uploaded_again(candidate_client, upload):
    content = pdf_bytes('Nguyen Van An - CV tai len lai sau khi xoa, Python')
    first = upload(SimpleUploadedFile('a.pdf', content)).data['id']
    candidate_client.delete(url(first))

    assert upload(SimpleUploadedFile('a.pdf', content)).status_code == 201


# ---------------------------------------------------------------- xem / tải file
def test_view_and_download_cv(candidate_client, upload):
    content = pdf_bytes('Nguyen Van An - Frontend Developer, ReactJS')
    cv_id = upload(SimpleUploadedFile('CV Nguyễn Văn An.pdf', content)).data['id']

    inline = candidate_client.get(url(cv_id, 'file'))
    attachment = candidate_client.get(url(cv_id, 'file') + '?download=1')

    assert inline.status_code == 200
    assert inline['Content-Type'] == 'application/pdf'
    assert inline['Content-Disposition'].startswith('inline')
    assert b''.join(inline.streaming_content) == content
    assert attachment['Content-Disposition'].startswith('attachment')
    assert "filename*=utf-8''CV%20Nguy%E1%BB%85n" in attachment['Content-Disposition']


def test_cv_file_is_not_publicly_served(upload, cv_upload, api_client):
    cv = CV.objects.get(pk=upload(cv_upload()).data['id'])

    assert cv.file.url is None  # PrivateMediaStorage: không có URL công khai
    assert api_client.get(url(cv.id, 'file')).status_code == 401


# ---------------------------------------------------------------- domain event (điểm mở rộng cho AI)
def test_domain_events_are_sent_after_commit(candidate_client, cv_upload, django_capture_on_commit_callbacks):
    received = []

    def receiver(signal, cv, **kwargs):
        received.append((signal, cv.parse_status))

    for sig in (signals.cv_uploaded, signals.cv_parsed, signals.cv_deleted):
        sig.connect(receiver, dispatch_uid=f'test-{id(sig)}')
    try:
        with django_capture_on_commit_callbacks(execute=True):
            cv_id = candidate_client.post(CVS, {'file': cv_upload()}, format='multipart').data['id']
        with django_capture_on_commit_callbacks(execute=True):
            candidate_client.delete(url(cv_id))
    finally:
        for sig in (signals.cv_uploaded, signals.cv_parsed, signals.cv_deleted):
            sig.disconnect(dispatch_uid=f'test-{id(sig)}')

    assert [sig for sig, _ in received] == [signals.cv_uploaded, signals.cv_parsed, signals.cv_deleted]
    assert received[1][1] == 'completed'


def test_parse_command_processes_pending_cvs(make_candidate):
    from django.core.management import call_command

    _, cv = make_candidate()  # CV tạo trực tiếp (như dữ liệu cũ): chưa bóc tách
    assert cv.parse_status == 'pending'

    call_command('parse_cvs', stdout=io.StringIO())

    cv.refresh_from_db()
    assert cv.parse_status == 'failed'  # nội dung giả '%PDF-1.4 test cv' không phải PDF hợp lệ
    assert cv.parse_error


def test_other_candidate_upload_is_independent(upload, make_candidate):
    """Cùng một file, hai ứng viên khác nhau đều upload được (kiểm tra trùng chỉ trong phạm vi một ứng viên)."""
    content = pdf_bytes('Mau CV chung tai tu mang, Python Django')
    upload(SimpleUploadedFile('a.pdf', content))
    other, _ = make_candidate()

    res = upload(SimpleUploadedFile('a.pdf', content), client=client_for(other.user))

    assert res.status_code == 201
