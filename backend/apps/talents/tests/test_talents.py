from datetime import timedelta

import pytest
from django.utils import timezone

from apps.applications import services as application_services
from apps.catalog.models import Location
from apps.cvs.models import CV
from apps.invitations import services as invitation_services
from conftest import client_for

pytestmark = pytest.mark.django_db


def url(job, query=''):
    return f'/api/v1/employer/jobs/{job.id}/suggested-candidates/{query}'


def pool_url(query=''):
    return f'/api/v1/employer/talents/{query}'


def cv_url(profile):
    return f'/api/v1/employer/talents/{profile.id}/cv/'


def names(res):
    return [item['candidate']['full_name'] for item in res.data['results']]


@pytest.fixture
def sales_job(make_job):
    return make_job(
        title='Nhân viên kinh doanh', skills=('Bán hàng', 'Đàm phán', 'Excel'), level='staff', min_years_experience=1,
        location_id=Location.objects.get(slug='ha-noi').id,
    )


def test_suggestions_are_ranked_and_explained(employer_client, sales_job, make_talent):
    hanoi = Location.objects.get(slug='ha-noi')
    # CV PDF font chuẩn mất dấu tiếng Việt: "ban hang" vẫn khớp kỹ năng "Bán hàng"
    make_talent('Kinh nghiem ban hang B2B, DAM PHAN hop dong, thanh thao Excel', full_name='An', current_level='staff',
                location=hanoi)
    make_talent('Ky nang: Excel', full_name='Bình')
    make_talent('Lap trinh Python, Django', full_name='Cường')  # không khớp kỹ năng nào: không hiện

    res = employer_client.get(url(sales_job))

    assert res.status_code == 200
    assert names(res) == ['An', 'Bình']
    best, weak = res.data['results']
    assert best['score'] == 100
    assert best['breakdown'] == {'skills': 60, 'experience': 20, 'level': 10, 'location': 10}
    assert best['matched_skills'] == ['Bán hàng', 'Đàm phán', 'Excel']
    assert best['missing_skills'] == []
    assert 'Cùng địa điểm Hà Nội' in best['reasons']
    assert best['application_id'] is None and best['invitation'] is None
    assert best['cv']['parse_status'] == 'completed'
    assert 'email' not in best['candidate']
    # Bình: 1/3 kỹ năng (20) + kinh nghiệm (20) + chưa khai cấp bậc, địa điểm (5 + 5)
    assert weak['score'] == 50
    assert weak['missing_skills'] == ['Bán hàng', 'Đàm phán']
    assert 'Thiếu kỹ năng bắt buộc: Bán hàng, Đàm phán' in weak['reasons']


def test_skill_matching_uses_aliases_and_whole_words(employer_client, make_job, make_talent):
    job = make_job(skills=('React', 'Java'))
    make_talent('3 nam lam viec voi ReactJS va JavaScript', full_name='Frontend')  # ReactJS là tên gọi khác của React

    item = employer_client.get(url(job)).data['results'][0]

    assert item['matched_skills'] == ['React']
    assert item['missing_skills'] == ['Java']  # "JavaScript" không được tính là "Java"


def test_only_discoverable_candidates_are_suggested(employer_client, sales_job, make_talent, make_job, other_recruiter):
    make_talent('ban hang', full_name='Công khai')
    make_talent('ban hang', is_public=False, full_name='Riêng tư')
    applicant, applicant_cv = make_talent('ban hang', is_public=False, full_name='Đã ứng tuyển')
    application = application_services.submit_application(candidate=applicant, job=sales_job, cv=applicant_cv)
    elsewhere, elsewhere_cv = make_talent('ban hang', is_public=False, full_name='Nộp công ty khác')
    other_job = make_job(company=other_recruiter.company, created_by=other_recruiter.user)
    application_services.submit_application(candidate=elsewhere, job=other_job, cv=elsewhere_cv)
    inactive, _ = make_talent('ban hang', full_name='Đã khóa')
    inactive.user.is_active = False
    inactive.user.save()

    res = employer_client.get(url(sales_job))

    assert sorted(names(res)) == ['Công khai', 'Đã ứng tuyển']
    applied = next(i for i in res.data['results'] if i['candidate']['full_name'] == 'Đã ứng tuyển')
    assert applied['application_id'] == str(application.id)
    assert names(employer_client.get(url(sales_job, '?hide_applied=true'))) == ['Công khai']


def test_filters_by_keyword_and_min_score(employer_client, sales_job, make_talent):
    make_talent('ban hang, dam phan, excel', full_name='Nguyễn Văn An', headline='Nhân viên kinh doanh')
    make_talent('excel', full_name='Trần Bình')

    assert names(employer_client.get(url(sales_job, '?q=kinh doanh'))) == ['Nguyễn Văn An']
    assert names(employer_client.get(url(sales_job, '?min_score=60'))) == ['Nguyễn Văn An']
    assert employer_client.get(url(sales_job, '?min_score=101')).status_code == 400


def test_candidate_without_default_cv_is_skipped(employer_client, sales_job, make_talent):
    profile, cv = make_talent('ban hang', full_name='Không có CV mặc định')
    cv.is_default = False
    cv.save()

    assert employer_client.get(url(sales_job)).data['count'] == 0


def test_includes_invitation_of_the_job(employer_client, recruiter, sales_job, make_job, make_talent):
    profile, _ = make_talent('ban hang')
    invitation_services.send_invitation(recruiter=recruiter, candidate=profile, job=make_job(), message='Mời')

    assert employer_client.get(url(sales_job)).data['results'][0]['invitation'] is None  # thư của tin khác

    invitation = invitation_services.send_invitation(recruiter=recruiter, candidate=profile, job=sales_job, message='Mời')
    item = employer_client.get(url(sales_job)).data['results'][0]

    assert item['invitation']['id'] == str(invitation.id)
    assert item['invitation']['status'] == 'pending'
    assert item['invitation']['job']['title'] == 'Nhân viên kinh doanh'


def test_talent_pool_lists_only_public_cvs(employer_client, sales_job, make_talent):
    make_talent('ban hang', full_name='Công khai')
    applicant, applicant_cv = make_talent('ban hang', is_public=False, full_name='Đã ứng tuyển')
    application_services.submit_application(candidate=applicant, job=sales_job, cv=applicant_cv)
    _, cv = make_talent('ban hang', full_name='Không có CV chính')
    CV.objects.filter(pk=cv.pk).update(is_default=False)
    inactive, _ = make_talent('ban hang', full_name='Đã khóa')
    inactive.user.is_active = False
    inactive.user.save()

    res = employer_client.get(pool_url())

    assert res.status_code == 200
    assert names(res) == ['Công khai']
    item = res.data['results'][0]
    assert item['cv']['title'] == 'CV' and item['invitation'] is None
    assert 'email' not in item['candidate']


def test_talent_pool_search_and_filters(employer_client, make_talent):
    hanoi = Location.objects.get(slug='ha-noi')
    make_talent('Ke toan tong hop, MISA', full_name='Lê Cúc', headline='Kế toán', current_level='staff', location=hanoi)
    make_talent('Ban hang B2B', full_name='Trần An', headline='Nhân viên kinh doanh', current_level='manager')

    # Nội dung CV PDF mất dấu tiếng Việt vẫn tìm được bằng từ khóa có dấu
    assert names(employer_client.get(pool_url('?q=tổng hợp'))) == ['Lê Cúc']
    assert names(employer_client.get(pool_url('?q=kinh doanh'))) == ['Trần An']
    assert names(employer_client.get(pool_url(f'?location_id={hanoi.id}'))) == ['Lê Cúc']
    assert names(employer_client.get(pool_url('?level=manager'))) == ['Trần An']
    assert employer_client.get(pool_url('?level=boss')).status_code == 400


def test_talent_pool_orders_by_cv_update_and_shows_latest_invitation(employer_client, recruiter, other_recruiter,
                                                                    make_job, make_talent):
    old, old_cv = make_talent('ban hang', full_name='Cũ')
    make_talent('ban hang', full_name='Mới')
    CV.objects.filter(pk=old_cv.pk).update(updated_at=timezone.now() - timedelta(days=3))
    invitation_services.send_invitation(recruiter=recruiter, candidate=old, job=make_job(title='Kế toán'), message='Mời')
    latest = invitation_services.send_invitation(
        recruiter=recruiter, candidate=old, job=make_job(title='Thủ kho'), message='Mời'
    )

    res = employer_client.get(pool_url())

    assert names(res) == ['Mới', 'Cũ']
    assert res.data['results'][1]['invitation']['id'] == str(latest.id)
    assert res.data['results'][1]['invitation']['job']['title'] == 'Thủ kho'
    # Thư của công ty khác không hiện
    assert client_for(other_recruiter.user).get(pool_url()).data['results'][1]['invitation'] is None


def test_talent_pool_is_for_employers(candidate_client):
    assert candidate_client.get(pool_url()).status_code == 403


def test_scoped_to_company_and_employer_role(employer_client, candidate_client, make_job, other_recruiter):
    foreign_job = make_job(company=other_recruiter.company, created_by=other_recruiter.user)

    assert employer_client.get(url(foreign_job)).status_code == 404
    assert candidate_client.get(url(foreign_job)).status_code == 403


def test_view_cv_of_discoverable_candidate(employer_client, other_recruiter, sales_job, make_talent):
    public, _ = make_talent('ban hang')
    private, _ = make_talent('ban hang', is_public=False)
    applicant, applicant_cv = make_talent('ban hang', is_public=False)
    application_services.submit_application(candidate=applicant, job=sales_job, cv=applicant_cv)

    res = employer_client.get(cv_url(public))

    assert res.status_code == 200
    assert b''.join(res.streaming_content) == b'%PDF-1.4 test cv'
    assert 'attachment' in employer_client.get(cv_url(public) + '?download=1')['Content-Disposition']
    assert employer_client.get(cv_url(private)).status_code == 404
    assert employer_client.get(cv_url(applicant)).status_code == 200
    # Công ty khác không thấy ứng viên chỉ ứng tuyển vào ACME
    assert client_for(other_recruiter.user).get(cv_url(applicant)).status_code == 404
