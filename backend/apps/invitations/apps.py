from django.apps import AppConfig


class InvitationsConfig(AppConfig):
    name = 'apps.invitations'
    label = 'invitations'
    verbose_name = 'Thư mời ứng tuyển'

    def ready(self):
        from apps.applications.signals import application_submitted

        from .receivers import on_application_submitted

        application_submitted.connect(on_application_submitted, dispatch_uid='invitations.on_application_submitted')
