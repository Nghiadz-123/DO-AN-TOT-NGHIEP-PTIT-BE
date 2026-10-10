"""Mở rộng danh mục cho nền tảng tuyển dụng đa ngành nghề (không chỉ công nghệ thông tin).

- Ngành nghề: bổ sung các ngành phổ biến; gộp 2 ngành con của CNTT về "Công nghệ thông tin" để CNTT
  là một ngành ngang hàng các ngành khác; đổi tên vài ngành cho rõ phạm vi.
- Kỹ năng: bổ sung kỹ năng của kinh doanh, marketing, kế toán, nhân sự, kỹ thuật, y tế, giáo dục, dịch vụ...
"""
import importlib

from django.db import migrations

from common.utils import vn_slugify

skill_slug = importlib.import_module('apps.catalog.migrations.0002_seed_catalog').skill_slug

IT_INDUSTRY = 'Công nghệ thông tin'
MERGED_INTO_IT = ['Phát triển phần mềm', 'Trí tuệ nhân tạo & Dữ liệu']

# tên cũ -> tên mới
RENAMED_INDUSTRIES = {
    'Viễn thông': 'Điện tử - Viễn thông',
    'Sản xuất': 'Sản xuất - Vận hành',
    'Bất động sản - Xây dựng': 'Bất động sản',
    'Du lịch - Khách sạn': 'Du lịch - Nhà hàng - Khách sạn',
}

NEW_INDUSTRIES = [
    'Kinh doanh - Bán hàng',
    'Chăm sóc khách hàng',
    'Hành chính - Văn phòng',
    'Nhân sự',
    'Kế toán - Kiểm toán',
    'Bảo hiểm',
    'Luật - Pháp lý',
    'Thiết kế - Mỹ thuật',
    'Báo chí - Biên tập',
    'Xây dựng - Kiến trúc',
    'Cơ khí - Chế tạo',
    'Điện - Năng lượng',
    'Xuất nhập khẩu',
    'Thực phẩm - Đồ uống',
    'Dệt may - Da giày',
    'Nông - Lâm - Ngư nghiệp',
    'Hóa chất - Môi trường',
    'Lao động phổ thông',
]

# (tên, nhóm, aliases). Tên không chứa dấu phẩy (frontend tách nhiều kỹ năng theo dấu phẩy).
NEW_SKILLS = [
    # Kinh doanh - Chăm sóc khách hàng
    ('Bán hàng', 'domain', ['Sales', 'Kỹ năng bán hàng']),
    ('Telesales', 'domain', ['Bán hàng qua điện thoại']),
    ('Đàm phán', 'soft', ['Negotiation', 'Thương lượng']),
    ('Chăm sóc khách hàng', 'domain', ['Customer Service', 'CSKH']),
    ('Phát triển thị trường', 'domain', ['Business Development']),
    ('Quản lý cửa hàng', 'domain', ['Store Management']),
    ('CRM', 'tool', ['Customer Relationship Management']),
    # Marketing - Truyền thông - Thiết kế
    ('Digital Marketing', 'domain', ['Marketing online']),
    ('Content Marketing', 'domain', ['Viết content', 'Copywriting']),
    ('SEO', 'domain', ['Search Engine Optimization']),
    ('Facebook Ads', 'tool', ['Quảng cáo Facebook', 'Meta Ads']),
    ('Google Ads', 'tool', ['Quảng cáo Google', 'Google Adwords']),
    ('Quản trị mạng xã hội', 'domain', ['Social Media', 'Social Media Marketing']),
    ('Tổ chức sự kiện', 'domain', ['Event Management']),
    ('Biên tập nội dung', 'domain', ['Biên tập viên', 'Editing']),
    ('Thiết kế đồ họa', 'technical', ['Graphic Design']),
    ('Photoshop', 'tool', ['Adobe Photoshop']),
    ('Illustrator', 'tool', ['Adobe Illustrator']),
    ('Dựng video', 'technical', ['Video Editing', 'Edit video']),
    ('Chụp ảnh', 'technical', ['Photography']),
    # Văn phòng - Nhân sự - Kế toán - Tài chính - Pháp lý
    ('Tin học văn phòng', 'tool', ['MS Office', 'Microsoft Office']),
    ('Word', 'tool', ['Microsoft Word']),
    ('PowerPoint', 'tool', ['Microsoft PowerPoint']),
    ('Soạn thảo văn bản', 'domain', []),
    ('Tuyển dụng', 'domain', ['Recruitment', 'Talent Acquisition']),
    ('C&B', 'domain', ['Tiền lương - Phúc lợi', 'Compensation & Benefits', 'Lương thưởng']),
    ('Đào tạo nội bộ', 'domain', ['L&D', 'Training']),
    ('Luật lao động', 'domain', ['Bộ luật Lao động']),
    ('Kế toán tổng hợp', 'domain', ['General Accounting']),
    ('Kế toán thuế', 'domain', ['Khai báo thuế', 'Tax Accounting']),
    ('Báo cáo tài chính', 'domain', ['Financial Reporting', 'BCTC']),
    ('Kiểm toán', 'domain', ['Audit']),
    ('MISA', 'tool', ['Phần mềm MISA']),
    ('Phân tích tài chính', 'domain', ['Financial Analysis']),
    ('Thẩm định tín dụng', 'domain', ['Credit Appraisal']),
    ('Tư vấn tài chính', 'domain', ['Financial Advisory']),
    ('Tư vấn pháp lý', 'domain', ['Legal Advisory']),
    ('Soạn thảo hợp đồng', 'domain', ['Contract Drafting']),
    # Kỹ thuật - Sản xuất - Xây dựng
    ('AutoCAD', 'tool', ['CAD']),
    ('SolidWorks', 'tool', []),
    ('Revit', 'tool', ['Autodesk Revit']),
    ('Đọc bản vẽ kỹ thuật', 'technical', ['Đọc bản vẽ']),
    ('Vận hành máy CNC', 'technical', ['CNC']),
    ('Hàn công nghiệp', 'technical', ['Hàn điện', 'Welding']),
    ('Điện công nghiệp', 'technical', []),
    ('PLC', 'technical', ['Lập trình PLC']),
    ('Bảo trì thiết bị', 'technical', ['Bảo trì máy móc', 'Maintenance']),
    ('Quản lý chất lượng', 'domain', ['QA/QC', 'QC', 'Quality Control']),
    ('ISO 9001', 'domain', ['ISO']),
    ('Lean', 'domain', ['Lean Manufacturing', '5S', 'Kaizen']),
    ('An toàn lao động', 'domain', ['HSE', 'An toàn vệ sinh lao động']),
    ('Giám sát thi công', 'domain', ['Giám sát công trình']),
    ('Dự toán công trình', 'domain', ['Dự toán', 'Bóc tách khối lượng']),
    # Logistics - Xuất nhập khẩu - Vận tải
    ('Thủ tục hải quan', 'domain', ['Khai báo hải quan', 'Customs Clearance']),
    ('Chứng từ xuất nhập khẩu', 'domain', ['Chứng từ XNK', 'Import-Export Documentation']),
    ('Quản lý kho', 'domain', ['Warehouse Management', 'Thủ kho']),
    ('Quản lý chuỗi cung ứng', 'domain', ['Supply Chain', 'SCM']),
    ('Giấy phép lái xe B2', 'domain', ['Bằng lái B2', 'Bằng B2']),
    ('Giấy phép lái xe C', 'domain', ['Bằng lái C', 'Bằng C']),
    # Y tế - Dược
    ('Điều dưỡng', 'technical', ['Chăm sóc người bệnh', 'Nursing']),
    ('Sơ cấp cứu', 'technical', ['First Aid', 'Cấp cứu']),
    ('Tư vấn dược', 'domain', ['Dược lâm sàng', 'Pharmacy']),
    ('Chứng chỉ hành nghề dược', 'domain', ['CCHN dược']),
    ('Xét nghiệm', 'technical', ['Kỹ thuật viên xét nghiệm']),
    # Giáo dục
    ('Giảng dạy', 'domain', ['Teaching', 'Dạy học']),
    ('Soạn giáo án', 'domain', ['Lesson Planning']),
    ('IELTS', 'language', []),
    ('TOEIC', 'language', []),
    # Nhà hàng - Khách sạn - Du lịch
    ('Lễ tân', 'domain', ['Receptionist', 'Front Office']),
    ('Nấu ăn', 'technical', ['Đầu bếp', 'Chef']),
    ('Pha chế', 'technical', ['Bartender', 'Barista']),
    ('Phục vụ nhà hàng', 'domain', ['Waiter', 'F&B Service']),
    ('Buồng phòng', 'domain', ['Housekeeping']),
    ('Hướng dẫn du lịch', 'domain', ['Tour Guide']),
    # Kỹ năng mềm - Quản lý - Ngoại ngữ
    ('Thuyết trình', 'soft', ['Presentation']),
    ('Lãnh đạo', 'soft', ['Leadership', 'Quản lý đội nhóm']),
    ('Quản lý dự án', 'domain', ['Project Management']),
    ('Tư duy phản biện', 'soft', ['Critical Thinking']),
    ('Chịu áp lực công việc', 'soft', ['Làm việc dưới áp lực', 'Work under pressure']),
    ('Tỉ mỉ', 'soft', ['Cẩn thận', 'Attention to detail']),
    ('Tiếng Pháp', 'language', ['French']),
    ('Tiếng Đức', 'language', ['German']),
]


def forwards(apps, schema_editor):
    Industry = apps.get_model('catalog', 'Industry')
    Skill = apps.get_model('catalog', 'Skill')
    Job = apps.get_model('jobs', 'Job')
    Company = apps.get_model('employers', 'Company')

    it, _ = Industry.objects.get_or_create(slug=vn_slugify(IT_INDUSTRY), defaults={'name': IT_INDUSTRY})
    for name in MERGED_INTO_IT:
        child = Industry.objects.filter(slug=vn_slugify(name)).first()
        if child is None:
            continue
        # Chuyển tin tuyển dụng / công ty (kể cả bản đã xóa mềm) sang ngành cha trước khi xóa ngành con
        Job._base_manager.filter(industry=child).update(industry=it)
        Company._base_manager.filter(industry=child).update(industry=it)
        child.delete()

    for old, new in RENAMED_INDUSTRIES.items():
        Industry.objects.filter(slug=vn_slugify(old)).update(name=new, slug=vn_slugify(new))

    for name in NEW_INDUSTRIES:
        Industry.objects.get_or_create(slug=vn_slugify(name), defaults={'name': name})

    for name, category, aliases in NEW_SKILLS:
        Skill.objects.get_or_create(
            slug=skill_slug(name),
            defaults={'name': name, 'category': category, 'aliases': aliases, 'is_verified': True},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0002_seed_catalog'),
        ('jobs', '0001_initial'),
        ('employers', '0001_initial'),
    ]

    # Không hoàn tác: ngành con đã gộp không tách lại được
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
