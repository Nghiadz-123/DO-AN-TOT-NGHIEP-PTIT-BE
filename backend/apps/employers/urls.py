from django.urls import path

from .views import CompanyLogoView, CompanyView, EmployerRegisterView, RecruiterProfileView

urlpatterns = [
    path('employer/register/', EmployerRegisterView.as_view(), name='employer-register'),
    path('employer/profile/', RecruiterProfileView.as_view(), name='employer-profile'),
    path('employer/company/', CompanyView.as_view(), name='employer-company'),
    path('employer/company/logo/', CompanyLogoView.as_view(), name='employer-company-logo'),
]
