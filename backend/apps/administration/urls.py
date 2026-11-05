from django.urls import path

from .views import (
    AdminCompanyDetailView,
    AdminCompanyListView,
    AdminJobDetailView,
    AdminJobListView,
    AdminOverviewView,
    AdminUserDetailView,
    AdminUserListView,
)

urlpatterns = [
    path('admin/overview/', AdminOverviewView.as_view(), name='admin-overview'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<uuid:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/companies/', AdminCompanyListView.as_view(), name='admin-companies'),
    path('admin/companies/<uuid:company_id>/', AdminCompanyDetailView.as_view(), name='admin-company-detail'),
    path('admin/jobs/', AdminJobListView.as_view(), name='admin-jobs'),
    path('admin/jobs/<uuid:job_id>/', AdminJobDetailView.as_view(), name='admin-job-detail'),
]
