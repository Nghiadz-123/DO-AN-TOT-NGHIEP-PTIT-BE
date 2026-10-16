"""API AI của ứng viên. LLM được thay bằng FakeLLM (không gọi Gemini thật):
- generate_json trả kết quả soạn sẵn theo prompt (bóc tách CV / chấm điểm / gợi ý / đánh giá);
- embed đếm số lần xuất hiện của vài cụm từ (bỏ dấu) nên văn bản cùng ngành nghề có cosine cao.
"""
import pytest

from apps.ai.llm import factory
from apps.ai.llm.base import JSONResult, LLMProvider
from apps.ai.models import CVAnalysis, CVEmbedding, JobEmbedding, JobMatch
from apps.ai.nlp.preprocessing import normalize_for_match
from apps.ai.prompts.cv_analysis import PARSE_CV_SYSTEM, SCORE_CV_SYSTEM
from apps.ai.prompts.cv_suggestion import SUGGEST_CV_SYSTEM
from apps.ai.prompts.job_recommendation import MATCH_SYSTEM
from apps.jobs.models import Job
from conftest import client_for

pytestmark = pytest.mark.django_db

ANALYSES = '/api/v1/candidate/cv-analyses/'
VOCABULARY = ['ban hang', 'khach hang', 'ke toan', 'thue', 'dieu duong', 'benh nhan', 'excel']
SALES_CV = 'Nguyễn Văn A\nNhân viên bán hàng, 3 năm kinh nghiệm tại cửa hàng điện máy\nKỹ năng: bán hàng, Excel'


def score_url(cv):
    return f'/api/v1/candidate/cvs/{cv.id}/analysis/score/'


def suggest_url(cv):
    return f'/api/v1/candidate/cvs/{cv.id}/analysis/suggestions/'


def jobs_url(cv, query=''):
    return f'/api/v1/candidate/cvs/{cv.id}/recommended-jobs/{query}'


def evaluate_url(cv, job):
    return f'/api/v1/candidate/cvs/{cv.id}/recommended-jobs/{job.id}/evaluate/'


class FakeLLM(LLMProvider):
    embed_model = 'fake-embedding'

    def __init__(self):
        self.profile = {
            'full_name': 'Nguyễn Văn A', 'email': 'a@test.com', 'phone': '0912345678', 'title': 'Nhân viên bán hàng',
            'summary': 'Bán hàng và chăm sóc khách hàng', 'years_of_experience': 3,
            'skills': ['Bán hàng', 'chăm sóc khách hàng'],
            'experiences': [{'company': 'Điện máy XYZ', 'position': 'Nhân viên bán hàng', 'start': '2022', 'end': None}],
        }
        self.score = {
            'total': 74, 'breakdown': {'completeness': 18, 'experience': 20, 'skills': 15, 'projects': 6, 'presentation': 15},
            'strengths': ['Có số liệu doanh số'], 'weaknesses': ['Thiếu mục tiêu nghề nghiệp'],
        }
        self.suggestions = {
            'suggestions': [
                {'section': 'Kỹ năng', 'issue': 'Thiếu kỹ năng tin học', 'suggestion': 'Bổ sung Excel',
                 'priority': 'medium', 'jd_refs': [1, 9]},
                {'section': 'Kinh nghiệm', 'issue': 'Thiếu số liệu', 'suggestion': 'Nêu doanh số đạt được',
                 'example_before': 'Bán hàng', 'example_after': 'Đạt 120% doanh số', 'priority': 'high', 'jd_refs': ['#2']},
            ],
            'missing_keywords': ['Kế toán thuế', 'Kế toán thuế', ''],
        }
        self.match = {'score': 90, 'matched_skills': ['Bán hàng'], 'missing_skills': [], 'reason': 'Rất phù hợp'}
        self.prompts = []  # (system, user) đã gửi
        self.embedded = []  # mỗi lần gọi embed: danh sách văn bản

    def generate_json(self, system, user):
        self.prompts.append((system, user))
        data = {PARSE_CV_SYSTEM: self.profile, SCORE_CV_SYSTEM: self.score, SUGGEST_CV_SYSTEM: self.suggestions,
                MATCH_SYSTEM: self.match}[system]
        return JSONResult(data=data, model='fake-chat')

    def embed(self, texts):
        self.embedded.append(list(texts))
        return [[normalize_for_match(text).count(term) for term in VOCABULARY] + [0.1] for text in texts]

    def systems(self):
        return [system for system, _ in self.prompts]


@pytest.fixture
def llm(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(factory, 'get_llm', lambda: fake)
    return fake


@pytest.fixture
def talent(make_talent):
    profile, cv = make_talent(SALES_CV)
    return client_for(profile.user), cv


@pytest.fixture
def jobs(make_job):
    return {
        'sales': make_job(
            title='Nhân viên bán hàng', description='Tư vấn và bán hàng cho khách hàng tại cửa hàng',
            requirements='Kinh nghiệm bán hàng\nGiao tiếp tốt với khách hàng', skills=('Bán hàng', 'Đàm phán'),
        ),
        'accounting': make_job(
            title='Kế toán tổng hợp', description='Kế toán thuế, báo cáo tài chính',
            requirements='Thành thạo Excel', skills=('Kế toán', 'Excel'),
        ),
        'nursing': make_job(
            title='Điều dưỡng viên', description='Chăm sóc bệnh nhân nội trú', requirements='Có chứng chỉ hành nghề',
            skills=('Điều dưỡng',),
        ),
        'draft': make_job(title='Nhân viên bán hàng (bản nháp)', publish=False, skills=('Bán hàng',)),
    }


# ------------------------------------------------------------------------------------------ chấm điểm CV
def test_score_cv_saves_score_and_profile(llm, talent):
    client, cv = talent

    res = client.post(score_url(cv))

    assert res.status_code == 200
    score = res.data['score']
    assert score['total'] == 74
    assert [(c['key'], c['score'], c['max']) for c in score['breakdown']] == [
        ('completeness', 18, 20), ('experience', 20, 25), ('skills', 15, 20), ('projects', 6, 15),
        ('presentation', 15, 20),
    ]
    assert score['strengths'] == ['Có số liệu doanh số']
    assert res.data['suggestions'] is None
    # Bóc tách hồ sơ chạy song song cùng lúc chấm điểm: kỹ năng được chuẩn hóa chữ thường
    assert res.data['profile']['skills'] == ['bán hàng', 'chăm sóc khách hàng']
    assert sorted(llm.systems()) == sorted([PARSE_CV_SYSTEM, SCORE_CV_SYSTEM])

    listed = client.get(ANALYSES)
    assert listed.status_code == 200
    assert [item['cv_id'] for item in listed.data] == [str(cv.id)]
    assert listed.data[0]['score']['total'] == 74

    # Chấm lại: hồ sơ đã có (văn bản CV không đổi) nên chỉ gọi lại bước chấm điểm
    llm.prompts.clear()
    client.post(score_url(cv))
    assert llm.systems() == [SCORE_CV_SYSTEM]


def test_score_is_clamped_and_total_recomputed(llm, talent):
    client, cv = talent
    llm.score = {'total': 150, 'breakdown': {'completeness': 35, 'experience': '-4', 'skills': '12.6'}, 'strengths': 'x'}

    res = client.post(score_url(cv))

    breakdown = {c['key']: c['score'] for c in res.data['score']['breakdown']}
    assert breakdown == {'completeness': 20, 'experience': 0, 'skills': 13, 'projects': 0, 'presentation': 0}
    assert res.data['score']['total'] == 33
    assert res.data['score']['strengths'] == []


def test_invalid_model_output_returns_502(llm, talent):
    client, cv = talent
    llm.score = {'message': 'không có điểm'}

    res = client.post(score_url(cv))

    assert res.status_code == 502
    assert res.data['code'] == 'ai_invalid_output'
    assert CVAnalysis.objects.get(cv=cv).score_total is None


def test_cv_must_be_parsed_first(llm, make_candidate):
    profile, cv = make_candidate()  # parse_status = pending

    res = client_for(profile.user).post(score_url(cv))

    assert res.status_code == 409
    assert res.data['code'] == 'cv_not_ready'
    assert llm.prompts == []


def test_ai_not_configured(talent):
    client, cv = talent  # settings test: GEMINI_API_KEY rỗng, không thay LLM giả

    res = client.post(score_url(cv))

    assert res.status_code == 503
    assert res.data['code'] == 'ai_not_configured'


def test_only_own_cv_and_candidates_only(llm, talent, make_talent, employer_client):
    client, cv = talent
    other_profile, other_cv = make_talent('Điều dưỡng viên 5 năm kinh nghiệm chăm sóc bệnh nhân', full_name='B')
    client_for(other_profile.user).post(score_url(other_cv))

    assert client.post(score_url(other_cv)).status_code == 404
    assert client.get(jobs_url(other_cv)).status_code == 404
    assert client.get(ANALYSES).data == []
    assert employer_client.post(score_url(cv)).status_code == 403


# ------------------------------------------------------------------------------------------ gợi ý việc làm
def test_recommend_open_jobs_by_similarity_and_skills(llm, talent, jobs):
    client, cv = talent

    res = client.get(jobs_url(cv))

    assert res.status_code == 200
    titles = [item['job']['title'] for item in res.data]
    assert titles[0] == 'Nhân viên bán hàng'
    assert 'Nhân viên bán hàng (bản nháp)' not in titles  # chỉ gợi ý tin đang tuyển
    best = res.data[0]
    assert best['matched_skills'] == ['Bán hàng'] and best['missing_skills'] == ['Đàm phán']
    assert best['skill_overlap'] == 0.5
    assert best['score'] == round(60 * best['similarity'] + 40 * 0.5)
    assert 'Đáp ứng 1/2 kỹ năng bắt buộc: Bán hàng' in best['reasons']
    assert best['ai_evaluation'] is None
    # Excel có trong văn bản CV (không có trong kỹ năng LLM bóc tách) vẫn được tính
    accounting = next(item for item in res.data if item['job']['title'] == 'Kế toán tổng hợp')
    assert accounting['matched_skills'] == ['Excel']
    assert res.data[0]['score'] > accounting['score']

    assert len(client.get(jobs_url(cv, '?limit=1')).data) == 1


def test_job_vectors_are_cached_and_refreshed_when_job_changes(llm, talent, jobs):
    client, cv = talent
    client.get(jobs_url(cv))
    assert JobEmbedding.objects.count() == 3 and CVEmbedding.objects.filter(cv=cv).exists()
    llm.embedded.clear()

    client.get(jobs_url(cv))
    assert llm.embedded == []  # không có gì mới: dùng lại vector đã lưu

    Job.objects.filter(pk=jobs['nursing'].pk).update(title='Điều dưỡng trưởng')
    client.get(jobs_url(cv))
    assert len(llm.embedded) == 1 and len(llm.embedded[0]) == 1  # chỉ embedding lại tin vừa sửa
    assert 'Điều dưỡng trưởng' in llm.embedded[0][0]


def test_evaluate_job_with_ai_and_reuse_result(llm, talent, jobs):
    client, cv = talent
    client.get(jobs_url(cv))

    res = client.post(evaluate_url(cv, jobs['accounting']))

    assert res.status_code == 200
    assert res.data['ai_evaluation']['score'] == 90
    assert res.data['ai_evaluation']['reason'] == 'Rất phù hợp'
    item = res.data
    assert item['score'] == round(0.5 * 90 + 30 * item['similarity'] + 20 * item['skill_overlap'])
    match_prompt = next(user for system, user in llm.prompts if system == MATCH_SYSTEM)
    assert 'Kế toán tổng hợp' in match_prompt and 'a@test.com' not in match_prompt  # không gửi thông tin liên hệ

    listed = {i['job']['id']: i for i in client.get(jobs_url(cv)).data}
    assert listed[str(jobs['accounting'].id)]['ai_evaluation']['score'] == 90
    # Tin đổi nội dung: kết quả đánh giá cũ không còn hiệu lực
    Job.objects.filter(pk=jobs['accounting'].pk).update(requirements='Thành thạo phần mềm MISA')
    listed = {i['job']['id']: i for i in client.get(jobs_url(cv)).data}
    assert listed[str(jobs['accounting'].id)]['ai_evaluation'] is None

    assert client.post(evaluate_url(cv, jobs['draft'])).status_code == 404


# ------------------------------------------------------------------------------------------ gợi ý sửa CV
def test_suggestions_use_target_job_and_nearest_jobs(llm, talent, jobs):
    client, cv = talent
    target = jobs['accounting']

    res = client.post(suggest_url(cv), {'job_id': str(target.id)}, format='json')

    assert res.status_code == 200
    data = res.data['suggestions']
    references = data['reference_jobs']
    assert {key: references[0][key] for key in ('id', 'title', 'company', 'is_target')} == {
        'id': str(target.id), 'title': 'Kế toán tổng hợp', 'company': 'ACME', 'is_target': True,
    }
    # Tin mục tiêu + các việc làm được gợi ý (cùng điểm và thứ tự với trang Việc làm phù hợp)
    recommended = client.get(jobs_url(cv)).data
    others = [item for item in recommended if item['job']['id'] != str(target.id)]
    assert [(r['id'], r['score']) for r in references[1:]] == [(i['job']['id'], i['score']) for i in others]
    assert references[1]['title'] == 'Nhân viên bán hàng'
    assert data['target_job_id'] == str(target.id)
    # Gợi ý ưu tiên cao đứng trước; số thứ tự JD (#1, #2) đổi thành id tin, số không có trong prompt bị bỏ
    high, medium = data['items']
    assert high['priority'] == 'high' and high['job_ids'] == [references[1]['id']]
    assert medium['job_ids'] == [str(target.id)]
    assert data['missing_keywords'] == ['Kế toán thuế']

    prompt = next(user for system, user in llm.prompts if system == SUGGEST_CV_SYSTEM)
    assert 'JD #1 (JD MỤC TIÊU do ứng viên chọn)' in prompt and 'Kế toán tổng hợp' in prompt
    # Mỗi tin kèm điểm phù hợp và kỹ năng CV đã có / còn thiếu; tổng hợp kỹ năng còn thiếu của các tin phù hợp
    assert '"match_score"' in prompt and '"cv_missing_skills": ["Đàm phán"]' in prompt
    assert 'KỸ NĂNG CV CÒN THIẾU LẶP LẠI NHIỀU NHẤT' in prompt and 'Đàm phán (1 JD)' in prompt


def test_suggestions_send_the_top_recommended_jobs(llm, talent, make_job):
    client, cv = talent
    for i in range(22):
        make_job(title=f'Nhân viên bán hàng {i}', skills=('Bán hàng',))

    res = client.post(suggest_url(cv), {}, format='json')

    references = res.data['suggestions']['reference_jobs']
    recommended = client.get(jobs_url(cv)).data
    assert len(references) == len(recommended) == 20  # mặc định 20 việc làm, cũng là số tin gửi cho AI
    assert [r['id'] for r in references] == [i['job']['id'] for i in recommended]
    prompt = next(user for system, user in llm.prompts if system == SUGGEST_CV_SYSTEM)
    assert 'JD #20:' in prompt and 'JD #21:' not in prompt and 'MỤC TIÊU' not in prompt


def test_suggestions_without_target_job(llm, talent):
    client, cv = talent  # chưa có tin nào: AI gợi ý theo chất lượng CV nói chung

    res = client.post(suggest_url(cv), {}, format='json')

    assert res.status_code == 200
    assert res.data['suggestions']['reference_jobs'] == []
    assert all(item['job_ids'] == [] for item in res.data['suggestions']['items'])
    assert 'CÁC JD THAM CHIẾU' not in llm.prompts[-1][1]


def test_suggestion_target_job_must_be_visible(llm, talent, jobs):
    client, cv = talent

    res = client.post(suggest_url(cv), {'job_id': str(jobs['draft'].id)}, format='json')

    assert res.status_code == 404


# ------------------------------------------------------------------------------------------ xóa CV
def test_deleting_cv_removes_ai_data(llm, talent, jobs, django_capture_on_commit_callbacks):
    client, cv = talent
    client.post(score_url(cv))
    client.post(evaluate_url(cv, jobs['sales']))
    assert CVAnalysis.objects.filter(cv=cv).exists() and JobMatch.objects.filter(cv=cv).exists()

    with django_capture_on_commit_callbacks(execute=True):  # cv_deleted được phát sau commit
        assert client.delete(f'/api/v1/candidate/cvs/{cv.id}/').status_code == 204

    assert not CVAnalysis.objects.filter(cv=cv).exists()
    assert not CVEmbedding.objects.filter(cv=cv).exists()
    assert not JobMatch.objects.filter(cv=cv).exists()
    assert JobEmbedding.objects.exists()  # vector của tin vẫn dùng cho CV khác
