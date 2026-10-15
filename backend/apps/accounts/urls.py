from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminCompaniesView,
    AdminJobsView,
    AdminOverviewView,
    AdminUsersView,
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    SsoAdminView,
)

RefreshView = extend_schema_view(post=extend_schema(tags=['Auth']))(TokenRefreshView)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/token/refresh/', RefreshView.as_view(), name='auth-token-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('auth/sso-admin/', SsoAdminView.as_view(), name='auth-sso-admin'),
    # Admin API
    path('admin/overview/', AdminOverviewView.as_view(), name='admin-overview'),
    path('admin/users/', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/<uuid:user_id>/', AdminUsersView.as_view(), name='admin-user-detail'),
    path('admin/companies/', AdminCompaniesView.as_view(), name='admin-companies'),
    path('admin/companies/<uuid:company_id>/', AdminCompaniesView.as_view(), name='admin-company-detail'),
    path('admin/jobs/', AdminJobsView.as_view(), name='admin-jobs'),
    path('admin/jobs/<uuid:job_id>/', AdminJobsView.as_view(), name='admin-job-detail'),
]
