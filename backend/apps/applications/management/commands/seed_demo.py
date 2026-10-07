"""Tạo dữ liệu demo cho môi trường dev (giống dữ liệu mock của frontend).

    python manage.py seed_demo           # bỏ qua nếu đã có dữ liệu demo
    python manage.py seed_demo --reset   # xóa dữ liệu demo cũ rồi tạo lại

Nhà tuyển dụng demo (mật khẩu 123456, CHỈ dùng cho dev):
    recruiter@demo.com - TechViet Solutions (đã xác minh)
    hr@cloudnine.demo  - CloudNine Tech (chờ xác minh)
Ứng viên demo không đăng nhập được: API phía ứng viên thuộc giai đoạn sau. Hồ sơ ứng tuyển được tạo qua
đúng service `submit_application` / `change_status` mà API thật sử dụng.
"""
import hashlib
import textwrap
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.applications import services as application_services
from apps.applications.models import Application, ApplicationStatus as S, ApplicationStatusHistory
from apps.candidates.models import CandidateProfile
from apps.catalog.models import Industry, Location
from apps.cvs.models import CV, CVMimeType
from apps.employers import services as employer_services
from apps.employers.models import Company, Recruiter, VerificationStatus
from apps.jobs import services as job_services
from apps.jobs.models import Job
from common.utils import strip_accents

DEMO_PASSWORD = '123456'
MILLION = 1_000_000

COMPANIES = [
    {
        'email': 'recruiter@demo.com', 'full_name': 'Trần Thị Bình', 'phone': '0987 654 321', 'position': 'HR Manager',
        'company': {
            'name': 'TechViet Solutions', 'tax_code': '0109876543', 'website': 'https://techviet.example.com',
            'email': 'hr@techviet.example.com', 'phone': '024 3999 8888',
            'address': 'Tầng 12, tòa nhà Sông Đà, Phạm Hùng, Cầu Giấy', 'location': 'ha-noi',
            'industry': 'phat-trien-phan-mem', 'company_size': '51-200', 'founded_year': 2016,
            'description': 'TechViet Solutions phát triển nền tảng SaaS quản trị doanh nghiệp và các giải pháp '
                           'AI cho thị trường Việt Nam, với hơn 150 kỹ sư tại Hà Nội và TP. Hồ Chí Minh.',
        },
        'verified': True,
    },
    {
        'email': 'hr@cloudnine.demo', 'full_name': 'Lê Hoàng Nam', 'phone': '0905 111 222', 'position': 'Talent Acquisition',
        'company': {
            'name': 'CloudNine Tech', 'tax_code': '0401234567', 'website': 'https://cloudnine.example.com',
            'email': 'jobs@cloudnine.example.com', 'phone': '0236 3888 999',
            'address': '25 Bạch Đằng, Hải Châu', 'location': 'da-nang', 'industry': 'cong-nghe-thong-tin',
            'company_size': '11-50', 'founded_year': 2019,
            'description': 'CloudNine Tech cung cấp dịch vụ phát triển ứng dụng di động và hạ tầng cloud cho '
                           'khách hàng fintech trong và ngoài nước.',
        },
        'verified': False,
    },
]

BENEFITS = 'Lương tháng 13, thưởng theo hiệu quả công việc\nBảo hiểm đầy đủ theo luật lao động\n' \
           'Môi trường trẻ trung, được đào tạo và phát triển'

# key, email công ty, tiêu đề, tỉnh, job_type, work_mode, level, lương (triệu), kỹ năng, kinh nghiệm tối thiểu,
# mô tả, yêu cầu, hạn nộp (+ngày), trạng thái cuối, đăng cách đây (ngày)
JOBS = [
    ('fe', 'recruiter@demo.com', 'Frontend Developer (ReactJS)', 'ha-noi', 'full_time', 'onsite', 'junior', (15, 25),
     ['React', 'JavaScript', 'TypeScript', 'HTML', 'CSS', 'Redux', 'Git'], 1,
     'Tham gia phát triển nền tảng quản lý doanh nghiệp SaaS. Xây dựng giao diện web hiện đại, tối ưu hiệu năng '
     'và trải nghiệm người dùng.',
     'Ít nhất 1 năm kinh nghiệm với ReactJS\nNắm vững JavaScript/TypeScript, HTML, CSS\n'
     'Có kinh nghiệm quản lý state (Redux, Zustand...)\nBiết sử dụng Git, làm việc theo quy trình Agile',
     39, 'published', 17),
    ('be', 'recruiter@demo.com', 'Backend Developer (Python/Django)', 'ha-noi', 'full_time', 'hybrid', 'middle', (25, 40),
     ['Python', 'Django', 'REST API', 'PostgreSQL', 'Docker', 'Redis', 'Git'], 2,
     'Thiết kế và phát triển hệ thống API cho các sản phẩm thương mại điện tử, xử lý hàng triệu request mỗi ngày.',
     'Tối thiểu 2 năm kinh nghiệm Python/Django\nThành thạo thiết kế REST API, PostgreSQL\n'
     'Có kinh nghiệm Docker, Redis là lợi thế',
     54, 'published', 19),
    ('ai', 'recruiter@demo.com', 'AI/ML Engineer (NLP)', 'ho-chi-minh', 'full_time', 'onsite', 'senior', (40, 60),
     ['Python', 'Machine Learning', 'NLP', 'PyTorch', 'LLM', 'SQL'], 4,
     'Nghiên cứu và triển khai các mô hình xử lý ngôn ngữ tự nhiên, xây dựng chatbot và hệ thống gợi ý dựa trên LLM.',
     'Tối thiểu 4 năm kinh nghiệm Machine Learning\nHiểu sâu về NLP, Transformer, LLM\n'
     'Thành thạo PyTorch, có kinh nghiệm đưa mô hình lên production',
     64, 'published', 22),
    ('intern', 'recruiter@demo.com', 'Thực tập sinh ReactJS', 'ha-noi', 'internship', 'onsite', 'intern', (3, 5),
     ['JavaScript', 'React', 'HTML', 'CSS', 'Git'], 0,
     'Chương trình thực tập 3 tháng, được mentor 1-1 và có cơ hội trở thành nhân viên chính thức.',
     'Sinh viên năm 3, năm 4 ngành CNTT\nCó kiến thức cơ bản về JavaScript, HTML, CSS\n'
     'Đã từng làm dự án cá nhân với ReactJS là lợi thế',
     24, 'published', 12),
    ('data', 'recruiter@demo.com', 'Data Analyst', 'ha-noi', 'full_time', 'remote', 'middle', (20, 30),
     ['SQL', 'Python', 'Power BI', 'Excel', 'Statistics'], 2,
     'Phân tích dữ liệu kinh doanh, xây dựng dashboard báo cáo và đề xuất giải pháp tối ưu doanh thu.',
     'Tối thiểu 2 năm kinh nghiệm phân tích dữ liệu\nThành thạo SQL, Power BI hoặc Tableau\n'
     'Tư duy logic, kỹ năng trình bày tốt',
     44, 'published', 27),
    ('ba', 'recruiter@demo.com', 'Business Analyst', 'ha-noi', 'full_time', 'onsite', 'junior', (18, 28),
     ['SQL', 'Agile', 'Giao tiếp', 'Excel'], 1,
     'Làm cầu nối giữa khách hàng và đội phát triển, phân tích nghiệp vụ và viết tài liệu đặc tả.',
     'Ít nhất 1 năm kinh nghiệm BA\nKỹ năng giao tiếp, viết tài liệu tốt\nBiết SQL cơ bản là lợi thế',
     60, 'draft', 0),
    ('mobile', 'hr@cloudnine.demo', 'Mobile Developer (Flutter)', 'da-nang', 'full_time', 'onsite', 'junior', (15, 25),
     ['Flutter', 'Dart', 'Firebase', 'REST API', 'Git'], 1,
     'Phát triển ứng dụng di động đa nền tảng cho khách hàng trong lĩnh vực fintech.',
     'Ít nhất 1 năm kinh nghiệm Flutter\nCó ứng dụng đã phát hành trên store là lợi thế',
     34, 'published', 15),
    ('devops', 'hr@cloudnine.demo', 'DevOps Engineer', 'ho-chi-minh', 'full_time', 'hybrid', 'senior', (35, 55),
     ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Terraform'], 4,
     'Xây dựng và vận hành hạ tầng cloud, tự động hóa quy trình triển khai cho hơn 50 dịch vụ.',
     'Tối thiểu 4 năm kinh nghiệm DevOps\nThành thạo Kubernetes, AWS, Terraform',
     55, 'published', 25),
    ('qa', 'hr@cloudnine.demo', 'QA/Tester Fresher', 'ha-noi', 'full_time', 'onsite', 'fresher', (10, 15),
     ['Manual Testing', 'API Testing', 'SQL', 'Jira', 'Selenium'], 0,
     'Kiểm thử chức năng các sản phẩm web/mobile, viết test case và báo cáo lỗi.',
     'Tốt nghiệp ngành CNTT hoặc liên quan\nCẩn thận, tỉ mỉ, có tư duy phân tích',
     18, 'closed', 20),
    ('fullstack', 'hr@cloudnine.demo', 'Fullstack Developer (Node.js/React)', 'ha-noi', 'full_time', 'remote', 'middle',
     (25, 40), ['Node.js', 'React', 'TypeScript', 'MongoDB', 'REST API', 'Docker'], 2,
     'Phát triển end-to-end các tính năng cho nền tảng thương mại điện tử B2B.',
     'Tối thiểu 2 năm kinh nghiệm fullstack JavaScript\nThành thạo React và Node.js',
     49, 'published', 18),
]

EDUCATION = 'Học viện Công nghệ Bưu chính Viễn thông - Kỹ sư Công nghệ thông tin (2020 - 2025)'

# key, email, họ tên, sđt, headline, năm KN, level, tỉnh, tóm tắt, kỹ năng, kinh nghiệm, tên file CV
CANDIDATES = [
    ('an', 'candidate@demo.com', 'Nguyễn Văn An', '0912 345 678', 'Frontend Developer', '1.5', 'junior', 'ha-noi',
     'Lập trình viên frontend với hơn 1 năm kinh nghiệm ReactJS, yêu thích thiết kế giao diện.',
     'React, JavaScript, HTML, CSS, Git, Redux, Node.js',
     ['Frontend Developer - Công ty CP Phần mềm Sao Mai (03/2025 - nay): phát triển giao diện hệ thống quản lý '
      'bán hàng bằng ReactJS, tích hợp REST API.'],
     'NguyenVanAn_Frontend_CV.pdf'),
    ('cuc', 'cuc.le@demo.com', 'Lê Thị Cúc', '0901 111 220', 'Backend Developer', '3', 'middle', 'ha-noi',
     'Backend Developer 3 năm kinh nghiệm Python/Django, từng thiết kế hệ thống API phục vụ 200.000 người dùng. '
     'Mạnh về tối ưu truy vấn PostgreSQL và kiến trúc microservice.',
     'Python, Django, REST API, PostgreSQL, Docker, Redis, Git, Celery',
     ['Backend Developer - Công ty TNHH Giải pháp Số Việt (06/2023 - nay): xây dựng 40+ API cho ứng dụng thương '
      'mại điện tử, giảm 35% thời gian phản hồi nhờ Redis cache.',
      'Python Developer - Startup EduTech (01/2022 - 05/2023): phát triển hệ thống quản lý khóa học bằng Django.'],
     'LeThiCuc_Backend.pdf'),
    ('duc', 'duc.pham@demo.com', 'Phạm Minh Đức', '0902 111 221', 'Frontend Developer', '2', 'junior', 'ha-noi',
     'Frontend Developer 2 năm kinh nghiệm React/TypeScript, đam mê tối ưu hiệu năng và trải nghiệm người dùng.',
     'React, TypeScript, JavaScript, HTML, CSS, Next.js, Redux, Git, Jest',
     ['Frontend Developer - Công ty Công nghệ Bình Minh (08/2024 - nay): tối ưu bundle giúp giảm 45% thời gian '
      'tải trang, xây dựng design system dùng cho 3 sản phẩm.'],
     'PhamMinhDuc_CV.pdf'),
    ('ha', 'ha.hoang@demo.com', 'Hoàng Thu Hà', '0903 111 222', 'Web Developer', '0.5', 'fresher', 'ha-noi',
     'Sinh viên mới tốt nghiệp, mong muốn học hỏi và phát triển trong lĩnh vực web.',
     'JavaScript, HTML, CSS, Vue.js, Git',
     ['Thực tập sinh Web - Công ty Phần mềm Hoa Sen (01/2026 - 06/2026): tham gia làm giao diện trang quản trị.'],
     'HoangThuHa_CV.pdf'),
    ('huy', 'huy.vu@demo.com', 'Vũ Quốc Huy', '0904 111 223', 'AI Engineer', '4', 'senior', 'ho-chi-minh',
     'AI Engineer 4 năm kinh nghiệm NLP và LLM, đã triển khai chatbot chăm sóc khách hàng xử lý 10.000 hội '
     'thoại/ngày. Thành thạo PyTorch và các kỹ thuật fine-tuning.',
     'Python, Machine Learning, NLP, PyTorch, LLM, SQL, Docker, Django',
     ['AI Engineer - Công ty AI Việt (2022 - nay): fine-tune mô hình ngôn ngữ tiếng Việt, tăng 20% độ chính xác '
      'phân loại ý định.'],
     'VuQuocHuy_AI_Engineer.pdf'),
    ('linh', 'linh.do@demo.com', 'Đỗ Mai Linh', '0905 111 224', 'Data Analyst', '1', 'junior', 'ha-noi',
     'Chuyên viên phân tích dữ liệu 1 năm kinh nghiệm, thành thạo SQL và Power BI.',
     'SQL, Python, Excel, Power BI, Django, HTML',
     ['Data Analyst - Công ty Bán lẻ Xanh (09/2025 - nay): xây dựng 12 dashboard doanh số, tự động hóa báo cáo tuần.'],
     'DoMaiLinh_DataAnalyst.pdf'),
]

# job, ứng viên, nộp cách đây (ngày), các bước pipeline sau khi nộp, thư giới thiệu
APPLICATIONS = [
    ('fe', 'an', 15, [S.SCREENING], 'Em rất mong được đóng góp vào đội ngũ frontend của công ty.'),
    ('fe', 'duc', 3, [], 'Tôi có 2 năm kinh nghiệm React/TypeScript và rất quan tâm tới sản phẩm SaaS.'),
    ('fe', 'ha', 2, [], ''),
    ('fe', 'linh', 1, [], ''),
    ('be', 'cuc', 18, [S.SCREENING, S.INTERVIEW], 'Tôi có 3 năm kinh nghiệm Django, từng tối ưu hệ thống lớn.'),
    ('be', 'huy', 5, [], ''),
    ('be', 'linh', 16, [S.REJECTED], ''),
    ('ai', 'huy', 21, [S.SCREENING, S.INTERVIEW, S.OFFER], 'Tôi có kinh nghiệm triển khai LLM vào sản phẩm thực tế.'),
    ('ai', 'cuc', 20, [S.SCREENING], ''),
    ('intern', 'ha', 4, [], ''),
    ('data', 'linh', 25, [S.SCREENING], ''),
    ('mobile', 'an', 14, [S.REJECTED], ''),
]

STEP_NOTES = {
    S.SCREENING: 'CV phù hợp, chuyển sang vòng sàng lọc.',
    S.INTERVIEW: 'Mời phỏng vấn vòng 1 với trưởng nhóm kỹ thuật.',
    S.OFFER: 'Ứng viên đạt phỏng vấn, gửi đề nghị nhận việc.',
    S.REJECTED: '',
}
REJECTION_REASON = 'Kinh nghiệm chưa phù hợp với yêu cầu của vị trí.'


class Command(BaseCommand):
    help = 'Tạo dữ liệu demo cho nhà tuyển dụng (chỉ dùng ở môi trường dev).'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Xóa dữ liệu demo cũ rồi tạo lại')
        parser.add_argument('--force', action='store_true', help='Cho phép chạy khi DEBUG=False')

    def handle(self, *args, **options):
        if not settings.DEBUG and not options['force']:
            raise CommandError('seed_demo chỉ dành cho môi trường dev (DEBUG=True). Dùng --force nếu chắc chắn.')

        demo_emails = [c['email'] for c in COMPANIES] + [c[1] for c in CANDIDATES]
        if User.objects.filter(email__in=demo_emails).exists():
            if not options['reset']:
                self.stdout.write(self.style.WARNING('Dữ liệu demo đã tồn tại. Dùng --reset để tạo lại.'))
                return
            self._reset(demo_emails)

        with transaction.atomic():
            recruiters = self._create_employers()
            jobs = self._create_jobs(recruiters)
            candidates = self._create_candidates()
            count = self._create_applications(jobs, candidates, recruiters)

        self.stdout.write(self.style.SUCCESS(
            f'Đã tạo {len(recruiters)} nhà tuyển dụng, {len(jobs)} tin, {len(candidates)} ứng viên, {count} hồ sơ.'
        ))
        self.stdout.write(f'Đăng nhập: recruiter@demo.com / {DEMO_PASSWORD} (hoặc hr@cloudnine.demo)')

    # ------------------------------------------------------------------ reset
    def _reset(self, emails):
        users = User.objects.filter(email__in=emails)
        companies = Company.all_objects.filter(recruiters__user__in=users).distinct()
        company_ids = list(companies.values_list('id', flat=True))
        Application.objects.filter(job__company_id__in=company_ids).delete()
        Application.objects.filter(candidate__user__in=users).delete()
        Job.all_objects.filter(company_id__in=company_ids).delete()
        for cv in CV.all_objects.filter(candidate__user__in=users):
            folder = Path(cv.file.path).parent if cv.file else None
            cv.file.delete(save=False)
            cv.delete()
            if folder and folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
        Recruiter.objects.filter(company_id__in=company_ids).delete()
        for company in Company.all_objects.filter(id__in=company_ids):
            company.logo.delete(save=False)
            company.delete()
        users.delete()
        self.stdout.write('Đã xóa dữ liệu demo cũ.')

    # ------------------------------------------------------------------ employers & jobs
    def _create_employers(self):
        recruiters = {}
        for spec in COMPANIES:
            info = dict(spec['company'])
            recruiter = employer_services.register_employer(
                email=spec['email'], password=DEMO_PASSWORD, full_name=spec['full_name'],
                company_name=info.pop('name'), phone=spec['phone'], position=spec['position'],
            )
            info['location'] = Location.objects.get(slug=info['location'])
            info['industry'] = Industry.objects.get(slug=info['industry'])
            employer_services.update_company(recruiter.company, data=info)
            if spec['verified']:
                employer_services.set_verification(recruiter.company, status=VerificationStatus.VERIFIED, by=None)
            recruiters[spec['email']] = recruiter
        return recruiters

    def _create_jobs(self, recruiters):
        now = timezone.now()
        today = timezone.localdate()
        jobs = {}
        for (key, email, title, location, job_type, work_mode, level, salary, skills, min_years, description,
             requirements, deadline_days, final_status, published_days_ago) in JOBS:
            recruiter = recruiters[email]
            job = job_services.create_job(
                company=recruiter.company,
                created_by=recruiter.user,
                data={
                    'title': title, 'description': description, 'requirements': requirements, 'benefits': BENEFITS,
                    'job_type': job_type, 'work_mode': work_mode, 'level': level,
                    'min_years_experience': Decimal(min_years), 'salary_min': salary[0] * MILLION,
                    'salary_max': salary[1] * MILLION, 'headcount': 2 if key in ('fe', 'intern') else 1,
                    'location': Location.objects.get(slug=location), 'deadline': today + timedelta(days=deadline_days),
                },
                skills=[{'name': name} for name in skills],
                publish=final_status != 'draft',
            )
            if final_status == 'closed':
                job_services.close_job(job, by=recruiter.user)
            created_at = now - timedelta(days=published_days_ago, hours=2)
            Job.objects.filter(pk=job.pk).update(created_at=created_at, published_at=job.published_at and created_at)
            job.refresh_from_db()
            jobs[key] = job
        return jobs

    # ------------------------------------------------------------------ candidates & CV
    def _create_candidates(self):
        candidates = {}
        for (key, email, full_name, phone, headline, years, level, location, summary, skills, experience,
             filename) in CANDIDATES:
            user = User.objects.create_user(email=email, password=None, role=UserRole.CANDIDATE,
                                            full_name=full_name, phone=phone)
            profile = CandidateProfile.objects.create(
                user=user, headline=headline, years_of_experience=Decimal(years), current_level=level,
                location=Location.objects.get(slug=location), summary=summary, desired_position=headline,
            )
            pdf = build_pdf([
                ('name', full_name), ('title', headline), ('text', f'Email: {email}  |  Dien thoai: {phone}'),
                ('heading', 'GIOI THIEU'), ('text', summary),
                ('heading', 'KY NANG'), ('text', skills),
                ('heading', 'KINH NGHIEM'), *[('text', f'- {line}') for line in experience],
                ('heading', 'HOC VAN'), ('text', EDUCATION),
            ])
            cv = CV(candidate=profile, title=f'CV {headline}', original_filename=filename, mime_type=CVMimeType.PDF,
                    file_size=len(pdf), file_hash=hashlib.sha256(pdf).hexdigest(), language='vi', is_default=True)
            cv.file.save(filename, ContentFile(pdf), save=False)
            cv.save()
            candidates[key] = (profile, cv)
        return candidates

    # ------------------------------------------------------------------ applications
    def _create_applications(self, jobs, candidates, recruiters):
        now = timezone.now()
        for job_key, candidate_key, days_ago, steps, cover_letter in APPLICATIONS:
            job = jobs[job_key]
            profile, cv = candidates[candidate_key]
            recruiter_user = recruiters[job.created_by.email].user
            application = application_services.submit_application(
                candidate=profile, job=job, cv=cv, cover_letter=cover_letter
            )
            for step in steps:
                application = application_services.change_status(
                    application, to_status=step, by=recruiter_user, note=STEP_NOTES[step],
                    rejection_reason=REJECTION_REASON if step == S.REJECTED else '',
                )
            # Dàn mốc thời gian về quá khứ cho timeline giống thật
            applied_at = now - timedelta(days=days_ago, hours=3)
            history = list(application.status_history.order_by('id'))
            for index, entry in enumerate(history):
                at = min(applied_at + timedelta(days=2 * index), now - timedelta(hours=1))
                ApplicationStatusHistory.objects.filter(pk=entry.pk).update(created_at=at)
            Application.objects.filter(pk=application.pk).update(
                created_at=applied_at,
                status_changed_at=min(applied_at + timedelta(days=2 * (len(history) - 1)), now - timedelta(hours=1)),
            )
        return len(APPLICATIONS)


# ---------------------------------------------------------------------- PDF tối giản (không cần thư viện)
_PDF_STYLES = {'name': ('F2', 20), 'title': ('F1', 13), 'heading': ('F2', 12), 'text': ('F1', 10)}


def build_pdf(blocks) -> bytes:
    """PDF 1 trang, font Helvetica chuẩn. Font chuẩn không có dấu tiếng Việt nên nội dung được bỏ dấu."""
    lines, y = [], 800
    for style, text in blocks:
        font, size = _PDF_STYLES[style]
        if style == 'heading':
            y -= 10
        for line in textwrap.wrap(strip_accents(text), int(1000 / size)) or ['']:
            if y < 50:
                break
            escaped = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            lines.append(f'BT /{font} {size} Tf 50 {y} Td ({escaped}) Tj ET')
            y -= int(size * 1.5)
    content = '\n'.join(lines).encode('latin-1', 'replace')
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] '
        b'/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>',
        b'<< /Length %d >>\nstream\n' % len(content) + content + b'\nendstream',
    ]
    out = bytearray(b'%PDF-1.4\n')
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b'%d 0 obj\n' % number + body + b'\nendobj\n'
    xref_at = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objects) + 1)
    out += b''.join(b'%010d 00000 n \n' % offset for offset in offsets)
    out += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objects) + 1, xref_at)
    return bytes(out)
