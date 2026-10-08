from django.db.models import Q
from django_filters import rest_framework as filters

from apps.catalog.choices import JobLevel, JobType, WorkMode

from . import workflow
from .models import Job, JobStatus


class _JobAttributeFilter(filters.FilterSet):
    job_type = filters.ChoiceFilter(choices=JobType.choices)
    level = filters.ChoiceFilter(choices=JobLevel.choices)
    work_mode = filters.ChoiceFilter(choices=WorkMode.choices)
    location = filters.NumberFilter(field_name='location_id')

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
    q = filters.CharFilter(method='filter_q', label='Tìm theo vị trí, công ty, kỹ năng')

    def filter_q(self, queryset, name, value):
        value = value.strip()
        return queryset.filter(
            Q(title__icontains=value) | Q(company__name__icontains=value) | Q(job_skills__skill__name__icontains=value)
        ).distinct()
