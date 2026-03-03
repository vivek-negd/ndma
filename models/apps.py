from django.apps import AppConfig

class ModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'models'    
    def ready(self):
        """
        Register signal handlers when the app is ready.
        This ensures volunteer count updates happen automatically.
        """
        import models.signals  # noqa