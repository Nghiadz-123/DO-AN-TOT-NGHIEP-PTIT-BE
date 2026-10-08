from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Application, ApplicationStatus


class StatusInFilter(filters.BaseInFilter, filters.ChoiceFilter):
    """?status=applied,screening"""


class EmployerApplicationFilter(filters.FilterSet):
    job = filters.UUIDFilter(field_name='job_id')
    status = StatusInFilter(choices=ApplicationStatus.choices, lookup_expr='in')
    q = filters.CharFilter(method='filter_q', label='Tìm theo tên, email, số điện thoại, tiêu đề hồ sơ')

    class Meta:
        model = Application
        fields = []

    def filter_q(self, queryset, name, value):
        value = value.strip()
        return queryset.filter(
            Q(candidate__user__full_name__icontains=value)
            | Q(candidate__user__email__icontains=value)
            | Q(candidate__user__phone__icontains=value)
            | Q(candidate__headline__icontains=value)
        )


class CandidateApplicationFilter(filters.FilterSet):
    status = StatusInFilter(choices=ApplicationStatus.choices, lookup_expr='in')
    q = filters.CharFilter(method='filter_q', label='Tìm theo vị trí, tên công ty')

    class Meta:
        model = Application
        fields = []

    def filter_q(self, queryset, name, value):
        value = value.strip()
        return queryset.filter(Q(job__title__icontains=value) | Q(job__company__name__icontains=value))
