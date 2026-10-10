from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from django_filters import rest_framework as filters

from apps.catalog.choices import JobLevel, JobType, WorkMode
from apps.employers.models import Company

from . import workflow
from .models import Job, JobStatus

# Lọc theo thời gian đăng tin: giá trị là số ngày tính tới hiện tại
POSTED_WITHIN_CHOICES = [
    ('1', '24 giờ qua'),
    ('3', '3 ngày qua'),
    ('7', '7 ngày qua'),
    ('14', '14 ngày qua'),
    ('30', '30 ngày qua'),
]


class _JobAttributeFilter(filters.FilterSet):
    job_type = filters.ChoiceFilter(choices=JobType.choices)
    level = filters.ChoiceFilter(choices=JobLevel.choices)
    work_mode = filters.ChoiceFilter(choices=WorkMode.choices)
    location = filters.NumberFilter(field_name='location_id')
    industry = filters.NumberFilter(field_name='industry_id', label='Ngành nghề (id)')

    class Meta:
        model = Job
        fields = []


class EmployerJobFilter(_JobAttributeFilter):
    status = filters.ChoiceFilter(choices=JobStatus.choices, method='filter_status')
    q = filters.CharFilter(method='filter_q', label='Tìm theo tiêu đề')

    def filter_status(self, queryset, name, value):
        return queryset.filter(workflow.status_q(value))

    def filter_q(self, queryset, name, value):
        return queryset.filter(title__icontains=value.strip())


class PublicJobFilter(_JobAttributeFilter):
    q = filters.CharFilter(method='filter_q', label='Tìm theo vị trí, công ty, kỹ năng, ngành nghề')
    company = filters.UUIDFilter(field_name='company_id', label='Công ty (id) - tin đang tuyển của một công ty')
    posted_within = filters.ChoiceFilter(
        choices=POSTED_WITHIN_CHOICES, method='filter_posted_within', label='Đăng trong vòng (số ngày)'
    )

    def filter_posted_within(self, queryset, name, value):
        return queryset.filter(published_at__gte=timezone.now() - timedelta(days=int(value)))

    def filter_q(self, queryset, name, value):
        value = value.strip()
        return queryset.filter(
            Q(title__icontains=value)
            | Q(company__name__icontains=value)
            | Q(job_skills__skill__name__icontains=value)
            | Q(industry__name__icontains=value)
        ).distinct()


class PublicCompanyFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_q', label='Tìm theo tên công ty')
    industry = filters.NumberFilter(field_name='industry_id', label='Ngành nghề (id)')
    location = filters.NumberFilter(field_name='location_id', label='Tỉnh/thành phố (id)')

    class Meta:
        model = Company
        fields = []

    def filter_q(self, queryset, name, value):
        return queryset.filter(name__icontains=value.strip())
