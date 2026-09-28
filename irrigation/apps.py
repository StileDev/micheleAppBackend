from django.apps import AppConfig


class IrrigationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'irrigation'

    def ready(self):
        import irrigation.signals  # noqa: F401
