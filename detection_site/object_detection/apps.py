# Модуль отвечает за конфигурацию приложения Django.
# Он предоставляет метаданные для приложения `object_detection`, такие, как название приложения,
# основной класс конфигурации и другие настройки, связанные с приложением в контексте Django

from django.apps import AppConfig


class ObjectDetectionConfig(AppConfig):
    """
    Конфигурация приложения object_detection для Django.

    Attributes:
        default_auto_field (str): Поле, автоматически создаваемое для новых моделей.
        name (str): Имя приложения, используется для идентификации в Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'object_detection'
