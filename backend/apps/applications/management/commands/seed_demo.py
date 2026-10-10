"""Tạo dữ liệu demo đa ngành nghề cho môi trường dev.

    python manage.py seed_demo           # bỏ qua nếu đã có dữ liệu demo
    python manage.py seed_demo --reset   # xóa dữ liệu demo cũ rồi tạo lại

Nhà tuyển dụng demo (mật khẩu 123456, CHỈ dùng cho dev):
    recruiter@demo.com     - Công ty CP Bán lẻ Sao Việt (bán lẻ; tin kinh doanh, kế toán, nhân sự, IT...)
    tuyendung@anphat.demo  - Công ty CP Cơ khí Chính xác An Phát (cơ khí - sản xuất, chờ xác minh)
    tuyendung@hoaan.demo   - Bệnh viện Đa khoa Hòa An (y tế)
    tuyendung@ngoisao.demo - Hệ thống Anh ngữ Ngôi Sao (giáo dục)
    hr@bienxanh.demo       - Khách sạn Biển Xanh Nha Trang (du lịch - nhà hàng - khách sạn)
Ứng viên demo (cùng mật khẩu): candidate@demo.com (kinh doanh), cuc.le@demo.com (kế toán),
duc.pham@demo.com (cơ khí), ha.hoang@demo.com (điều dưỡng), huy.vu@demo.com, linh.do@demo.com
candidate@demo.com và ha.hoang@demo.com có sẵn vài việc làm / công ty yêu thích.
Tài khoản, CV (kèm bóc tách văn bản) và hồ sơ ứng tuyển được tạo qua đúng service mà API thật sử dụng
(`register_candidate`, `upload_cv`, `submit_application`, `change_status`).
"""
import textwrap
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.applications import services as application_services
from apps.applications.models import Application, ApplicationStatus as S, ApplicationStatusHistory
from apps.candidates import services as candidate_services
from apps.catalog.models import Industry, Location
from apps.cvs import services as cv_services
from apps.cvs.models import CV, CVMimeType
from apps.employers import services as employer_services
from apps.employers.models import Company, Recruiter, VerificationStatus
from apps.favorites import services as favorite_services
from apps.jobs import services as job_services
from apps.jobs.models import Job
from common.utils import strip_accents

DEMO_PASSWORD = '123456'
MILLION = 1_000_000

# Công ty ở nhiều ngành nghề khác nhau. industry/location: tên ngành, slug tỉnh trong danh mục.
COMPANIES = [
    {
        'email': 'recruiter@demo.com', 'full_name': 'Trần Thị Bình', 'phone': '0987 654 321',
        'position': 'Trưởng phòng Nhân sự',
        'company': {
            'name': 'Công ty CP Bán lẻ Sao Việt', 'tax_code': '0109876543', 'website': 'https://saoviet.example.com',
            'email': 'tuyendung@saoviet.example.com', 'phone': '024 3999 8888',
            'address': 'Số 89 Láng Hạ, Đống Đa', 'location': 'ha-noi',
            'industry': 'Bán lẻ - Hàng tiêu dùng', 'company_size': '1000+', 'founded_year': 2012,
            'description': 'Sao Việt sở hữu chuỗi hơn 120 siêu thị mini và cửa hàng tiện lợi tại Hà Nội, '
                           'TP. Hồ Chí Minh và các tỉnh miền Bắc, cùng hệ thống kho vận và kênh bán hàng trực tuyến.',
        },
        'verified': True,
    },
    {
        'email': 'tuyendung@anphat.demo', 'full_name': 'Lê Hoàng Nam', 'phone': '0905 111 222',
        'position': 'Chuyên viên tuyển dụng',
        'company': {
            'name': 'Công ty CP Cơ khí Chính xác An Phát', 'tax_code': '2301234567',
            'website': 'https://anphat.example.com', 'email': 'hr@anphat.example.com', 'phone': '0222 3777 666',
            'address': 'Lô C5, Khu công nghiệp Quế Võ', 'location': 'bac-ninh', 'industry': 'Cơ khí - Chế tạo',
            'company_size': '201-500', 'founded_year': 2008,
            'description': 'An Phát gia công linh kiện cơ khí chính xác và khuôn mẫu cho các doanh nghiệp FDI '
                           'ngành điện tử, ô tô; sản phẩm xuất khẩu sang Nhật Bản và Hàn Quốc.',
        },
        'verified': False,
    },
    {
        'email': 'tuyendung@hoaan.demo', 'full_name': 'Phan Thu Trang', 'phone': '0935 222 333',
        'position': 'Phó phòng Tổ chức cán bộ',
        'company': {
            'name': 'Bệnh viện Đa khoa Hòa An', 'tax_code': '0401122334', 'website': 'https://hoaan.example.com',
            'email': 'tuyendung@hoaan.example.com', 'phone': '0236 3666 555',
            'address': '120 Nguyễn Văn Linh, Hải Châu', 'location': 'da-nang', 'industry': 'Y tế - Dược phẩm',
            'company_size': '501-1000', 'founded_year': 2010,
            'description': 'Bệnh viện tư nhân 300 giường với 20 chuyên khoa, đạt chứng nhận quản lý chất lượng '
                           'ISO 9001:2015.',
        },
        'verified': True,
    },
    {
        'email': 'tuyendung@ngoisao.demo', 'full_name': 'Nguyễn Minh Tâm', 'phone': '0908 333 444',
        'position': 'Quản lý đào tạo',
        'company': {
            'name': 'Hệ thống Anh ngữ Ngôi Sao', 'tax_code': '0312345678', 'website': 'https://ngoisao.example.com',
            'email': 'jobs@ngoisao.example.com', 'phone': '028 3888 7777',
            'address': '45 Nguyễn Thị Minh Khai, Quận 1', 'location': 'ho-chi-minh',
            'industry': 'Giáo dục - Đào tạo', 'company_size': '51-200', 'founded_year': 2015,
            'description': '12 cơ sở đào tạo tiếng Anh giao tiếp và luyện thi IELTS cho học sinh, sinh viên '
                           'và người đi làm.',
        },
        'verified': True,
    },
    {
        'email': 'hr@bienxanh.demo', 'full_name': 'Võ Thị Mai', 'phone': '0914 444 555',
        'position': 'Trưởng bộ phận Nhân sự',
        'company': {
            'name': 'Khách sạn Biển Xanh Nha Trang', 'tax_code': '4201234567',
            'website': 'https://bienxanh.example.com', 'email': 'hr@bienxanh.example.com', 'phone': '0258 3555 444',
            'address': '68 Trần Phú, Nha Trang', 'location': 'khanh-hoa',
            'industry': 'Du lịch - Nhà hàng - Khách sạn', 'company_size': '201-500', 'founded_year': 2014,
            'description': 'Khách sạn 4 sao 220 phòng bên bờ biển Trần Phú, phục vụ khách du lịch trong nước '
                           'và quốc tế.',
        },
        'verified': True,
    },
]

# Email demo của phiên bản dữ liệu cũ (chỉ có công ty IT) - vẫn được xóa khi chạy --reset
LEGACY_DEMO_EMAILS = ['hr@cloudnine.demo']

BENEFITS = 'Lương tháng 13, thưởng theo hiệu quả công việc\nBảo hiểm đầy đủ theo luật lao động\n' \
           'Được đào tạo, có lộ trình thăng tiến rõ ràng'

SAO_VIET, AN_PHAT, HOA_AN, NGOI_SAO, BIEN_XANH = (c['email'] for c in COMPANIES)

# key, email công ty, tiêu đề, ngành nghề, tỉnh, job_type, work_mode, level, lương (triệu), kỹ năng,
# kinh nghiệm tối thiểu, mô tả, yêu cầu, hạn nộp (+ngày), trạng thái cuối, đăng cách đây (ngày)
JOBS = [
    ('sales', SAO_VIET, 'Nhân viên kinh doanh khách hàng doanh nghiệp', 'Kinh doanh - Bán hàng', 'ha-noi',
     'full_time', 'onsite', 'staff', (12, 25), ['Bán hàng', 'Đàm phán', 'Chăm sóc khách hàng', 'Tin học văn phòng'], 1,
     'Tìm kiếm và phát triển khách hàng doanh nghiệp (văn phòng, trường học, nhà máy) sử dụng dịch vụ cung ứng '
     'hàng tiêu dùng của Sao Việt. Thu nhập gồm lương cứng và hoa hồng theo doanh số.',
     'Ít nhất 1 năm kinh nghiệm bán hàng B2B hoặc bán hàng dự án\nKỹ năng giao tiếp, đàm phán tốt\n'
     'Có xe máy, sẵn sàng đi gặp khách hàng',
     39, 'published', 17),
    ('acc', SAO_VIET, 'Kế toán tổng hợp', 'Kế toán - Kiểm toán', 'ha-noi', 'full_time', 'onsite', 'staff', (15, 22),
     ['Kế toán tổng hợp', 'Kế toán thuế', 'Báo cáo tài chính', 'MISA', 'Excel'], 2,
     'Phụ trách hạch toán, đối chiếu công nợ, lập báo cáo thuế và báo cáo tài chính cho 3 công ty thành viên.',
     'Tốt nghiệp chuyên ngành Kế toán, Kiểm toán, Tài chính\nTối thiểu 2 năm kinh nghiệm kế toán tổng hợp\n'
     'Thành thạo MISA và Excel, nắm vững luật thuế hiện hành',
     54, 'published', 19),
    ('hr', SAO_VIET, 'Chuyên viên tuyển dụng', 'Nhân sự', 'ha-noi', 'full_time', 'onsite', 'staff', (12, 18),
     ['Tuyển dụng', 'Luật lao động', 'Giao tiếp', 'Tin học văn phòng'], 1,
     'Tuyển dụng nhân sự khối cửa hàng và văn phòng: đăng tin, sàng lọc hồ sơ, phỏng vấn, theo dõi thử việc.',
     'Ít nhất 1 năm kinh nghiệm tuyển dụng, ưu tiên ngành bán lẻ\nHiểu biết Bộ luật Lao động\n'
     'Giao tiếp tốt, chủ động trong công việc',
     44, 'published', 22),
    ('store', SAO_VIET, 'Cửa hàng trưởng', 'Bán lẻ - Hàng tiêu dùng', 'ho-chi-minh', 'full_time', 'onsite',
     'supervisor', (14, 20), ['Quản lý cửa hàng', 'Bán hàng', 'Lãnh đạo', 'Quản lý kho'], 2,
     'Quản lý vận hành cửa hàng tiện lợi: doanh số, hàng hóa, phân ca và đội ngũ 8 - 10 nhân viên.',
     'Tối thiểu 2 năm kinh nghiệm quản lý cửa hàng bán lẻ hoặc F&B\nKỹ năng lãnh đạo, xử lý tình huống tốt\n'
     'Chấp nhận làm việc theo ca',
     34, 'published', 15),
    ('region', SAO_VIET, 'Giám đốc kinh doanh khu vực miền Nam', 'Kinh doanh - Bán hàng', 'ho-chi-minh',
     'full_time', 'hybrid', 'director', (50, 80), ['Phát triển thị trường', 'Lãnh đạo', 'Đàm phán', 'Quản lý dự án'], 8,
     'Xây dựng chiến lược và chịu trách nhiệm doanh số toàn bộ hệ thống cửa hàng khu vực miền Nam.',
     'Tối thiểu 8 năm kinh nghiệm kinh doanh, trong đó 3 năm ở vị trí quản lý vùng\n'
     'Khả năng lãnh đạo đội ngũ lớn, đàm phán với đối tác\nTốt nghiệp Đại học khối Kinh tế, Quản trị kinh doanh',
     64, 'published', 25),
    ('intern', SAO_VIET, 'Thực tập sinh Marketing', 'Marketing - Truyền thông', 'ha-noi', 'internship', 'hybrid',
     'intern', (3, 5), ['Content Marketing', 'Quản trị mạng xã hội', 'Photoshop'], 0,
     'Hỗ trợ lên nội dung cho fanpage, website và các chương trình khuyến mãi của chuỗi cửa hàng. '
     'Thực tập 3 tháng, có cơ hội trở thành nhân viên chính thức.',
     'Sinh viên năm 3, năm 4 ngành Marketing, Truyền thông, Báo chí\n'
     'Viết tốt, sáng tạo; biết dùng Photoshop hoặc Canva là lợi thế',
     24, 'published', 12),
    ('it', SAO_VIET, 'Lập trình viên Web (ReactJS)', 'Công nghệ thông tin', 'ha-noi', 'full_time', 'hybrid', 'staff',
     (15, 25), ['React', 'JavaScript', 'HTML', 'CSS', 'Git'], 1,
     'Phát triển website bán hàng và hệ thống quản lý cửa hàng nội bộ của Sao Việt.',
     'Ít nhất 1 năm kinh nghiệm ReactJS\nNắm vững JavaScript, HTML, CSS\nBiết sử dụng Git',
     49, 'published', 27),
    ('cskh', SAO_VIET, 'Nhân viên chăm sóc khách hàng', 'Chăm sóc khách hàng', 'ha-noi', 'full_time', 'onsite',
     'staff', (8, 12), ['Chăm sóc khách hàng', 'Giao tiếp', 'Tin học văn phòng'], 0,
     'Tiếp nhận, giải đáp thắc mắc và xử lý khiếu nại của khách hàng qua tổng đài và fanpage.',
     'Giọng nói dễ nghe, kiên nhẫn\nTin học văn phòng cơ bản\nNhận sinh viên mới tốt nghiệp',
     60, 'draft', 0),
    ('warehouse', SAO_VIET, 'Nhân viên kho', 'Logistics - Vận tải', 'ha-noi', 'full_time', 'onsite', 'staff', (8, 11),
     ['Quản lý kho', 'Excel', 'Tỉ mỉ'], 0,
     'Nhập - xuất hàng, kiểm kê và sắp xếp hàng hóa tại kho tổng Gia Lâm.',
     'Sức khỏe tốt, trung thực, cẩn thận\nBiết Excel cơ bản là lợi thế',
     18, 'closed', 20),
    ('mech', AN_PHAT, 'Kỹ sư thiết kế cơ khí', 'Cơ khí - Chế tạo', 'bac-ninh', 'full_time', 'onsite', 'staff',
     (15, 22), ['AutoCAD', 'SolidWorks', 'Đọc bản vẽ kỹ thuật', 'Tiếng Anh'], 2,
     'Thiết kế khuôn mẫu, đồ gá và linh kiện cơ khí chính xác theo bản vẽ của khách hàng Nhật Bản.',
     'Tốt nghiệp Đại học ngành Cơ khí, Cơ điện tử\nTối thiểu 2 năm kinh nghiệm thiết kế bằng AutoCAD, SolidWorks\n'
     'Đọc hiểu tài liệu kỹ thuật tiếng Anh',
     55, 'published', 15),
    ('cnc', AN_PHAT, 'Công nhân vận hành máy CNC', 'Sản xuất - Vận hành', 'bac-ninh', 'full_time', 'onsite', 'staff',
     (8, 12), ['Vận hành máy CNC', 'Đọc bản vẽ kỹ thuật', 'An toàn lao động'], 0,
     'Vận hành máy phay, tiện CNC gia công linh kiện theo bản vẽ. Làm việc theo ca, được đào tạo từ đầu.',
     'Tốt nghiệp Trung cấp, Cao đẳng nghề Cơ khí là lợi thế\nĐọc được bản vẽ kỹ thuật cơ bản\n'
     'Chấp nhận làm ca, tăng ca',
     30, 'published', 10),
    ('qc', AN_PHAT, 'Trưởng nhóm QC', 'Sản xuất - Vận hành', 'bac-ninh', 'full_time', 'onsite', 'supervisor', (18, 25),
     ['Quản lý chất lượng', 'ISO 9001', 'Lean', 'Lãnh đạo'], 4,
     'Quản lý nhóm 12 nhân viên kiểm tra chất lượng, xây dựng quy trình kiểm soát chất lượng theo ISO 9001.',
     'Tối thiểu 4 năm kinh nghiệm QC trong nhà máy cơ khí, điện tử\nNắm vững ISO 9001, 5S, Kaizen\n'
     'Có kinh nghiệm quản lý nhóm',
     45, 'published', 25),
    ('nurse', HOA_AN, 'Điều dưỡng viên khoa Nội', 'Y tế - Dược phẩm', 'da-nang', 'full_time', 'onsite', 'staff',
     (9, 14), ['Điều dưỡng', 'Sơ cấp cứu', 'Giao tiếp', 'Chịu áp lực công việc'], 0,
     'Chăm sóc, theo dõi người bệnh nội trú và phối hợp với bác sĩ thực hiện y lệnh tại khoa Nội tổng hợp.',
     'Tốt nghiệp Cao đẳng, Đại học Điều dưỡng\nCó chứng chỉ hành nghề hoặc đang làm thủ tục cấp\n'
     'Tận tâm, chịu được áp lực, làm việc theo ca trực',
     40, 'published', 8),
    ('pharma', HOA_AN, 'Dược sĩ nhà thuốc bệnh viện', 'Y tế - Dược phẩm', 'da-nang', 'full_time', 'onsite', 'staff',
     (12, 18), ['Tư vấn dược', 'Chứng chỉ hành nghề dược', 'Tỉ mỉ'], 1,
     'Cấp phát thuốc theo đơn, tư vấn sử dụng thuốc cho người bệnh và quản lý xuất nhập tồn tại nhà thuốc.',
     'Tốt nghiệp Đại học Dược\nCó chứng chỉ hành nghề dược\nCẩn thận, tỉ mỉ, giao tiếp tốt',
     35, 'published', 14),
    ('teacher', NGOI_SAO, 'Giáo viên tiếng Anh (IELTS)', 'Giáo dục - Đào tạo', 'ho-chi-minh', 'part_time', 'onsite',
     'staff', (12, 20), ['Giảng dạy', 'IELTS', 'Thuyết trình', 'Soạn giáo án'], 1,
     'Giảng dạy các lớp luyện thi IELTS 5.0 - 7.0 vào buổi tối và cuối tuần, sĩ số tối đa 15 học viên.',
     'IELTS 7.5 trở lên\nCó ít nhất 1 năm kinh nghiệm giảng dạy\nPhát âm chuẩn, phong cách giảng dạy sinh động',
     50, 'published', 6),
    ('reception', BIEN_XANH, 'Nhân viên lễ tân', 'Du lịch - Nhà hàng - Khách sạn', 'khanh-hoa', 'full_time',
     'onsite', 'staff', (8, 12), ['Lễ tân', 'Tiếng Anh', 'Giao tiếp', 'Tin học văn phòng'], 0,
     'Đón tiếp, làm thủ tục nhận - trả phòng và hỗ trợ khách lưu trú tại quầy lễ tân.',
     'Tốt nghiệp Cao đẳng trở lên ngành Du lịch, Quản trị khách sạn\nGiao tiếp tiếng Anh tốt\n'
     'Chấp nhận làm việc theo ca',
     28, 'published', 9),
    ('chef', BIEN_XANH, 'Bếp trưởng nhà hàng Á', 'Du lịch - Nhà hàng - Khách sạn', 'khanh-hoa', 'full_time', 'onsite',
     'manager', (25, 35), ['Nấu ăn', 'Lãnh đạo', 'Chịu áp lực công việc'], 5,
     'Quản lý bếp Á của nhà hàng 200 chỗ: xây dựng thực đơn, kiểm soát chi phí nguyên liệu và an toàn thực phẩm.',
     'Tối thiểu 5 năm kinh nghiệm, trong đó 2 năm ở vị trí bếp trưởng hoặc bếp phó\n'
     'Có chứng chỉ nghề bếp và kiến thức an toàn vệ sinh thực phẩm\nKỹ năng quản lý đội ngũ',
     42, 'published', 21),
]

# Số lượng tuyển (mặc định 1)
HEADCOUNT = {'sales': 5, 'store': 3, 'intern': 2, 'cnc': 10, 'nurse': 3, 'reception': 2}

# key, email, họ tên, sđt, headline, năm KN, level, tỉnh, tóm tắt, kỹ năng, kinh nghiệm, học vấn, tên file CV
CANDIDATES = [
    ('an', 'candidate@demo.com', 'Nguyễn Văn An', '0912 345 678', 'Nhân viên kinh doanh', '1.5', 'staff', 'ha-noi',
     'Nhân viên kinh doanh hơn 1 năm kinh nghiệm bán hàng B2B, luôn đạt và vượt chỉ tiêu doanh số quý.',
     'Bán hàng, Đàm phán, Chăm sóc khách hàng, Tin học văn phòng, CRM',
     ['Nhân viên kinh doanh - Công ty TNHH Thiết bị Văn phòng Phú Gia (03/2025 - nay): phát triển 35 khách hàng '
      'doanh nghiệp mới, đạt 115% chỉ tiêu năm 2025.'],
     'Đại học Thương mại - Cử nhân Quản trị kinh doanh (2020 - 2024)',
     'NguyenVanAn_KinhDoanh_CV.pdf'),
    ('cuc', 'cuc.le@demo.com', 'Lê Thị Cúc', '0901 111 220', 'Kế toán tổng hợp', '3', 'staff', 'ha-noi',
     'Kế toán tổng hợp 3 năm kinh nghiệm tại doanh nghiệp thương mại, thành thạo quyết toán thuế và lập báo cáo '
     'tài chính.',
     'Kế toán tổng hợp, Kế toán thuế, Báo cáo tài chính, MISA, Excel',
     ['Kế toán tổng hợp - Công ty CP Thương mại Hà Thành (06/2023 - nay): lập báo cáo tài chính, quyết toán thuế '
      'TNDN cho 2 pháp nhân.',
      'Kế toán viên - Công ty TNHH Dịch vụ Kế toán Minh Tâm (07/2022 - 05/2023): hạch toán và kê khai thuế cho '
      '15 khách hàng.'],
     'Học viện Tài chính - Cử nhân Kế toán (2018 - 2022)',
     'LeThiCuc_KeToan.pdf'),
    ('duc', 'duc.pham@demo.com', 'Phạm Minh Đức', '0902 111 221', 'Kỹ sư cơ khí', '2', 'staff', 'bac-ninh',
     'Kỹ sư thiết kế cơ khí 2 năm kinh nghiệm thiết kế đồ gá, khuôn dập cho linh kiện điện tử.',
     'AutoCAD, SolidWorks, Đọc bản vẽ kỹ thuật, Tiếng Anh, Quản lý chất lượng',
     ['Kỹ sư thiết kế - Công ty TNHH Khuôn mẫu Đông Á (08/2024 - nay): thiết kế hơn 40 bộ đồ gá, giảm 15% thời '
      'gian gia công.'],
     'Đại học Bách khoa Hà Nội - Kỹ sư Cơ khí chế tạo máy (2019 - 2024)',
     'PhamMinhDuc_CoKhi_CV.pdf'),
    ('ha', 'ha.hoang@demo.com', 'Hoàng Thu Hà', '0903 111 222', 'Điều dưỡng', '0.5', 'fresher', 'da-nang',
     'Điều dưỡng mới tốt nghiệp, đã thực tập 6 tháng tại khoa Nội, mong muốn gắn bó lâu dài với bệnh viện.',
     'Điều dưỡng, Sơ cấp cứu, Giao tiếp, Tin học văn phòng',
     ['Thực tập điều dưỡng - Bệnh viện Đa khoa Bình Minh (01/2026 - 06/2026): chăm sóc người bệnh, theo dõi dấu '
      'hiệu sinh tồn.'],
     'Đại học Kỹ thuật Y - Dược Đà Nẵng - Cử nhân Điều dưỡng (2022 - 2026)',
     'HoangThuHa_DieuDuong_CV.pdf'),
    ('huy', 'huy.vu@demo.com', 'Vũ Quốc Huy', '0904 111 223', 'Quản lý kinh doanh khu vực', '9', 'manager',
     'ho-chi-minh',
     'Quản lý kinh doanh 9 năm trong ngành hàng tiêu dùng nhanh, quản lý đội ngũ 40 nhân viên bán hàng và mạng '
     'lưới 300 điểm bán.',
     'Bán hàng, Lãnh đạo, Phát triển thị trường, Đàm phán, Quản lý dự án',
     ['Quản lý kinh doanh khu vực - Công ty CP Hàng tiêu dùng Phương Nam (2021 - nay): tăng trưởng doanh số khu '
      'vực 25%/năm.',
      'Giám sát bán hàng - Công ty TNHH Thực phẩm Sài Gòn Xanh (2017 - 2021).'],
     'Đại học Kinh tế TP. Hồ Chí Minh - Cử nhân Quản trị kinh doanh (2013 - 2017)',
     'VuQuocHuy_QuanLyKinhDoanh.pdf'),
    ('linh', 'linh.do@demo.com', 'Đỗ Mai Linh', '0905 111 224', 'Chuyên viên nhân sự', '1', 'staff', 'ha-noi',
     'Chuyên viên nhân sự 1 năm kinh nghiệm tuyển dụng khối văn phòng và bán lẻ.',
     'Tuyển dụng, Luật lao động, Giao tiếp, Tin học văn phòng, C&B',
     ['Chuyên viên tuyển dụng - Công ty CP Chuỗi Cà phê Mộc (09/2025 - nay): tuyển 120 nhân sự cửa hàng trong '
      '6 tháng.'],
     'Đại học Lao động - Xã hội - Cử nhân Quản trị nhân lực (2021 - 2025)',
     'DoMaiLinh_NhanSu.pdf'),
]

# job, ứng viên, nộp cách đây (ngày), các bước pipeline sau khi nộp, thư giới thiệu
APPLICATIONS = [
    ('sales', 'an', 15, [S.SCREENING],
     'Tôi có hơn 1 năm kinh nghiệm bán hàng B2B và mong muốn phát triển cùng Sao Việt.'),
    ('sales', 'linh', 1, [], ''),
    ('store', 'an', 3, [], ''),
    ('store', 'huy', 14, [S.REJECTED], ''),
    ('region', 'huy', 5, [], 'Tôi có 9 năm kinh nghiệm quản lý kinh doanh khu vực trong ngành hàng tiêu dùng.'),
    ('acc', 'cuc', 18, [S.SCREENING, S.INTERVIEW, S.OFFER],
     'Tôi có 3 năm kinh nghiệm kế toán tổng hợp và quyết toán thuế.'),
    ('hr', 'linh', 20, [S.SCREENING, S.INTERVIEW], ''),
    ('mech', 'duc', 21, [S.SCREENING, S.INTERVIEW], 'Tôi đã có 2 năm thiết kế đồ gá cho khách hàng Nhật Bản.'),
    ('qc', 'duc', 4, [], ''),
    ('nurse', 'ha', 2, [], 'Em mong muốn được làm việc tại khoa Nội của bệnh viện.'),
    ('pharma', 'ha', 16, [S.REJECTED], ''),
]

# ứng viên, tin yêu thích, công ty yêu thích (có cả tin đã đóng để thấy trạng thái trên trang Yêu thích)
FAVORITES = [
    ('an', ['region', 'store', 'warehouse'], [SAO_VIET, BIEN_XANH]),
    ('ha', ['nurse', 'pharma'], [HOA_AN]),
]

STEP_NOTES = {
    S.SCREENING: 'Hồ sơ phù hợp, chuyển sang vòng sàng lọc.',
    S.INTERVIEW: 'Mời phỏng vấn vòng 1 với quản lý trực tiếp.',
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

        demo_emails = [c['email'] for c in COMPANIES] + [c[1] for c in CANDIDATES] + LEGACY_DEMO_EMAILS
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
            favorite_count = self._create_favorites(jobs, candidates, recruiters)

        self.stdout.write(self.style.SUCCESS(
            f'Đã tạo {len(recruiters)} nhà tuyển dụng, {len(jobs)} tin, {len(candidates)} ứng viên, {count} hồ sơ, '
            f'{favorite_count} lượt yêu thích.'
        ))
        self.stdout.write(f'Nhà tuyển dụng: recruiter@demo.com / {DEMO_PASSWORD} (hoặc tuyendung@anphat.demo, ...)')
        self.stdout.write(f'Ứng viên: candidate@demo.com / {DEMO_PASSWORD} (hoặc cuc.le@demo.com, ...)')

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
                try:
                    folder.rmdir()
                except OSError:  # Windows/OneDrive có thể đang giữ thư mục; thư mục rỗng để lại không ảnh hưởng
                    pass
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
            info['industry'] = Industry.objects.get(name=info['industry'])
            employer_services.update_company(recruiter.company, data=info)
            if spec['verified']:
                employer_services.set_verification(recruiter.company, status=VerificationStatus.VERIFIED, by=None)
            recruiters[spec['email']] = recruiter
        return recruiters

    def _create_jobs(self, recruiters):
        now = timezone.now()
        today = timezone.localdate()
        jobs = {}
        for (key, email, title, industry, location, job_type, work_mode, level, salary, skills, min_years,
             description, requirements, deadline_days, final_status, published_days_ago) in JOBS:
            recruiter = recruiters[email]
            job = job_services.create_job(
                company=recruiter.company,
                created_by=recruiter.user,
                data={
                    'title': title, 'description': description, 'requirements': requirements, 'benefits': BENEFITS,
                    'job_type': job_type, 'work_mode': work_mode, 'level': level,
                    'min_years_experience': Decimal(min_years), 'salary_min': salary[0] * MILLION,
                    'salary_max': salary[1] * MILLION, 'headcount': HEADCOUNT.get(key, 1),
                    'industry': Industry.objects.get(name=industry), 'location': Location.objects.get(slug=location),
                    'deadline': today + timedelta(days=deadline_days),
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
        for (key, email, full_name, phone, headline, years, level, location, summary, skills, experience, education,
             filename) in CANDIDATES:
            profile = candidate_services.register_candidate(
                email=email, password=DEMO_PASSWORD, full_name=full_name, phone=phone
            )
            candidate_services.update_candidate_profile(profile, data={
                'headline': headline, 'years_of_experience': Decimal(years), 'current_level': level,
                'location': Location.objects.get(slug=location), 'summary': summary, 'desired_position': headline,
            })
            pdf = build_pdf([
                ('name', full_name), ('title', headline), ('text', f'Email: {email}  |  Dien thoai: {phone}'),
                ('heading', 'GIOI THIEU'), ('text', summary),
                ('heading', 'KY NANG'), ('text', skills),
                ('heading', 'KINH NGHIEM'), *[('text', f'- {line}') for line in experience],
                ('heading', 'HOC VAN'), ('text', education),
            ])
            # Bóc tách văn bản chạy sau khi transaction của lệnh commit (như khi upload qua API)
            cv = cv_services.upload_cv(
                candidate=profile, file=ContentFile(pdf, name=filename), mime_type=CVMimeType.PDF,
                title=f'CV {headline}', language='vi',
            )
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

    # ------------------------------------------------------------------ favorites
    def _create_favorites(self, jobs, candidates, recruiters):
        count = 0
        for candidate_key, job_keys, company_emails in FAVORITES:
            profile, _ = candidates[candidate_key]
            for key in job_keys:
                count += favorite_services.add_favorite_job(profile, jobs[key])
            for email in company_emails:
                count += favorite_services.add_favorite_company(profile, recruiters[email].company)
        return count


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
