from django.apps import AppConfig

class NeuroaAppConfig(AppConfig):
    name = 'apps.neuroa_app'  # Chemin complet vers l'application
    verbose_name = 'Neuroa Application'  # Nom lisible de l'application

    def ready(self):
        # Code à exécuter lorsque l'application est prête
        pass
