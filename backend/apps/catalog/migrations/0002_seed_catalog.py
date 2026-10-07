"""Dữ liệu danh mục ban đầu: tỉnh/thành, ngành nghề, kỹ năng phổ biến."""
from django.db import migrations

from common.utils import vn_slugify

# 34 đơn vị hành chính cấp tỉnh (Nghị quyết 202/2025/QH15, hiệu lực 01/07/2025).
# 6 thành phố trực thuộc trung ương đứng đầu, sau đó 28 tỉnh theo thứ tự chữ cái.
LOCATIONS = [
    'Hà Nội', 'Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ', 'Huế',
    'An Giang', 'Bắc Ninh', 'Cà Mau', 'Cao Bằng', 'Đắk Lắk', 'Điện Biên', 'Đồng Nai', 'Đồng Tháp',
    'Gia Lai', 'Hà Tĩnh', 'Hưng Yên', 'Khánh Hòa', 'Lai Châu', 'Lâm Đồng', 'Lạng Sơn', 'Lào Cai',
    'Nghệ An', 'Ninh Bình', 'Phú Thọ', 'Quảng Ngãi', 'Quảng Ninh', 'Quảng Trị', 'Sơn La', 'Tây Ninh',
    'Thái Nguyên', 'Thanh Hóa', 'Tuyên Quang', 'Vĩnh Long',
]

# (tên, tên ngành cha)
INDUSTRIES = [
    ('Công nghệ thông tin', None),
    ('Phát triển phần mềm', 'Công nghệ thông tin'),
    ('Trí tuệ nhân tạo & Dữ liệu', 'Công nghệ thông tin'),
    ('Viễn thông', None),
    ('Thương mại điện tử', None),
    ('Tài chính - Ngân hàng', None),
    ('Giáo dục - Đào tạo', None),
    ('Y tế - Dược phẩm', None),
    ('Bán lẻ - Hàng tiêu dùng', None),
    ('Sản xuất', None),
    ('Logistics - Vận tải', None),
    ('Bất động sản - Xây dựng', None),
    ('Marketing - Truyền thông', None),
    ('Du lịch - Khách sạn', None),
    ('Tư vấn - Dịch vụ doanh nghiệp', None),
]

# (tên, nhóm, aliases)
SKILLS = [
    ('Python', 'technical', ['Python3']),
    ('Java', 'technical', []),
    ('JavaScript', 'technical', ['JS']),
    ('TypeScript', 'technical', ['TS']),
    ('C++', 'technical', ['CPP']),
    ('C#', 'technical', ['CSharp']),
    ('Go', 'technical', ['Golang']),
    ('PHP', 'technical', []),
    ('Kotlin', 'technical', []),
    ('Swift', 'technical', []),
    ('Dart', 'technical', []),
    ('SQL', 'technical', []),
    ('HTML', 'technical', ['HTML5']),
    ('CSS', 'technical', ['CSS3']),
    ('React', 'technical', ['ReactJS', 'React.js']),
    ('Next.js', 'technical', ['NextJS']),
    ('Vue.js', 'technical', ['Vue', 'VueJS']),
    ('Angular', 'technical', ['AngularJS']),
    ('Redux', 'technical', []),
    ('Node.js', 'technical', ['NodeJS', 'Node']),
    ('Express.js', 'technical', ['Express', 'ExpressJS']),
    ('Django', 'technical', []),
    ('Flask', 'technical', []),
    ('FastAPI', 'technical', []),
    ('Spring Boot', 'technical', ['Spring']),
    ('.NET', 'technical', ['dotnet', 'ASP.NET', 'ASP.NET Core']),
    ('Laravel', 'technical', []),
    ('Flutter', 'technical', []),
    ('React Native', 'technical', []),
    ('REST API', 'technical', ['RESTful API', 'RESTful', 'REST']),
    ('GraphQL', 'technical', []),
    ('Microservices', 'technical', ['Microservice']),
    ('PostgreSQL', 'technical', ['Postgres']),
    ('MySQL', 'technical', []),
    ('MongoDB', 'technical', ['Mongo']),
    ('Redis', 'technical', []),
    ('Elasticsearch', 'technical', []),
    ('Celery', 'technical', []),
    ('Firebase', 'technical', []),
    ('Docker', 'technical', []),
    ('Kubernetes', 'technical', ['K8s']),
    ('AWS', 'technical', ['Amazon Web Services']),
    ('Azure', 'technical', ['Microsoft Azure']),
    ('Google Cloud', 'technical', ['GCP']),
    ('Linux', 'technical', []),
    ('CI/CD', 'technical', []),
    ('Terraform', 'technical', []),
    ('Machine Learning', 'technical', ['ML']),
    ('Deep Learning', 'technical', ['DL']),
    ('NLP', 'technical', ['Natural Language Processing', 'Xử lý ngôn ngữ tự nhiên']),
    ('LLM', 'technical', ['Large Language Model']),
    ('PyTorch', 'technical', []),
    ('TensorFlow', 'technical', []),
    ('Pandas', 'technical', []),
    ('Data Analysis', 'technical', ['Phân tích dữ liệu']),
    ('Statistics', 'technical', ['Thống kê']),
    ('Manual Testing', 'technical', ['Kiểm thử thủ công']),
    ('Automation Testing', 'technical', ['Kiểm thử tự động']),
    ('API Testing', 'technical', []),
    ('Selenium', 'tool', []),
    ('Jest', 'tool', []),
    ('Git', 'tool', []),
    ('Jira', 'tool', []),
    ('Figma', 'tool', []),
    ('Power BI', 'tool', ['PowerBI']),
    ('Tableau', 'tool', []),
    ('Excel', 'tool', ['Microsoft Excel']),
    ('UI/UX Design', 'domain', ['UI/UX', 'UX/UI']),
    ('Agile', 'domain', ['Scrum']),
    ('Giao tiếp', 'soft', ['Communication']),
    ('Làm việc nhóm', 'soft', ['Teamwork']),
    ('Giải quyết vấn đề', 'soft', ['Problem Solving']),
    ('Quản lý thời gian', 'soft', ['Time Management']),
    ('Tiếng Anh', 'language', ['English']),
    ('Tiếng Nhật', 'language', ['Japanese']),
    ('Tiếng Hàn', 'language', ['Korean']),
    ('Tiếng Trung', 'language', ['Chinese']),
]


def skill_slug(name):
    # Giữ đồng bộ với apps.catalog.services.skill_slug (có test kiểm tra)
    text = ' '.join(name.split()).lower().replace('+', ' plus ').replace('#', ' sharp ').replace('.', ' dot ')
    return vn_slugify(text, 120)


def seed(apps, schema_editor):
    Location = apps.get_model('catalog', 'Location')
    Industry = apps.get_model('catalog', 'Industry')
    Skill = apps.get_model('catalog', 'Skill')

    for name in LOCATIONS:
        Location.objects.get_or_create(slug=vn_slugify(name), defaults={'name': name})

    industries = {}
    for name, parent in INDUSTRIES:
        industries[name], _ = Industry.objects.get_or_create(
            slug=vn_slugify(name), defaults={'name': name, 'parent': industries.get(parent)}
        )

    for name, category, aliases in SKILLS:
        Skill.objects.get_or_create(
            slug=skill_slug(name),
            defaults={'name': name, 'category': category, 'aliases': aliases, 'is_verified': True},
        )


class Migration(migrations.Migration):
    dependencies = [('catalog', '0001_initial')]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
