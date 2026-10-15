from django.apps import AppConfig


class MessagingConfig(AppConfig):
    name = 'apps.messaging'
    label = 'messaging'
    verbose_name = 'Tin nhắn'

    def ready(self):
        from apps.connections.signals import connection_accepted

        from .receivers import on_connection_accepted

        connection_accepted.connect(on_connection_accepted, dispatch_uid='messaging.on_connection_accepted')
