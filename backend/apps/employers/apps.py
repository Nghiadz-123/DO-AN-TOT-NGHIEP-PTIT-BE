from django.apps import AppConfig


class EmployersConfig(AppConfig):
    name = 'apps.employers'
    label = 'employers'
    verbose_name = 'Nhà tuyển dụng'

    def ready(self):
        from apps.accounts.models import UserRole
        from apps.accounts.registry import register_profile_provider

        from .serializers import build_employer_profile

        register_profile_provider(UserRole.EMPLOYER, build_employer_profile)
