"""Embedding tin tuyển dụng trước khi ứng viên dùng AI: tự động khi đăng / sửa tin và lệnh embed_jobs."""
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from apps.ai.llm import factory
from apps.ai.llm.exceptions import AIUnavailableError
from apps.ai.models import JobEmbedding
from apps.ai.tests.test_candidate_ai import FakeLLM
from apps.jobs import services as job_services

pytestmark = pytest.mark.django_db


@pytest.fixture
def llm(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(factory, 'get_llm', lambda: fake)
    return fake


def test_publishing_a_job_embeds_it(llm, make_job, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        job = make_job(title='Nhân viên bán hàng', skills=('Bán hàng',))

    assert JobEmbedding.objects.filter(job=job).exists()
    assert len(llm.embedded) == 1 and 'Nhân viên bán hàng' in llm.embedded[0][0]


def test_editing_re_embeds_only_when_embedded_content_changes(llm, make_job, future_date,
                                                              django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        job = make_job()
    llm.embedded.clear()

    with django_capture_on_commit_callbacks(execute=True):
        job_services.update_job(job, data={'deadline': future_date(60)})  # hạn nộp không nằm trong văn bản embedding
    assert llm.embedded == []

    with django_capture_on_commit_callbacks(execute=True):
        job_services.update_job(job, data={'title': 'Kế toán tổng hợp'})
    assert len(llm.embedded) == 1 and 'Kế toán tổng hợp' in llm.embedded[0][0]


def test_jobs_that_are_not_open_are_not_embedded(llm, make_job, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        job = make_job(publish=False)
        job_services.update_job(job, data={'title': 'Bản nháp đã sửa'})

    assert llm.embedded == [] and not JobEmbedding.objects.exists()


def test_embedding_failure_does_not_break_publishing(llm, make_job, django_capture_on_commit_callbacks):
    def fail(texts):
        raise AIUnavailableError()

    llm.embed = fail

    with django_capture_on_commit_callbacks(execute=True):
        job = make_job()

    assert job.status == 'published' and not JobEmbedding.objects.exists()


def test_publishing_without_ai_configured_still_works(make_job, django_capture_on_commit_callbacks):
    # Settings test: GEMINI_API_KEY rỗng, không thay LLM giả
    with django_capture_on_commit_callbacks(execute=True):
        job = make_job()

    assert job.status == 'published' and not JobEmbedding.objects.exists()


def test_embed_jobs_command_backfills_existing_jobs(llm, make_job):
    open_jobs = [make_job(title=f'Nhân viên {i}') for i in range(3)]
    make_job(title='Bản nháp', publish=False)  # callback đăng tin chưa chạy: tin có sẵn chưa có vector

    out = StringIO()
    call_command('embed_jobs', stdout=out)

    assert set(JobEmbedding.objects.values_list('job_id', flat=True)) == {job.pk for job in open_jobs}
    assert '3 tin đang tuyển, 3 tin vừa embedding, 0 tin đã có vector' in out.getvalue()
    assert len(llm.embedded) == 1 and len(llm.embedded[0]) == 3  # gộp một lần gọi API

    llm.embedded.clear()
    out = StringIO()
    call_command('embed_jobs', stdout=out)  # chạy lại: không tốn lượt gọi API
    assert llm.embedded == []
    assert '3 tin đang tuyển, 0 tin vừa embedding, 3 tin đã có vector' in out.getvalue()


def test_embed_jobs_command_reports_ai_errors(make_job):
    make_job()

    with pytest.raises(CommandError, match='chưa được cấu hình'):
        call_command('embed_jobs', stdout=StringIO())
