from django.apps import AppConfig


class CandidatesConfig(AppConfig):
    name = 'apps.candidates'
    label = 'candidates'
    verbose_name = 'Ứng viên'

    def ready(self):
        from apps.accounts.models import UserRole
        from apps.accounts.registry import register_profile_provider

        from .serializers import build_candidate_profile

        register_profile_provider(UserRole.CANDIDATE, build_candidate_profile)
