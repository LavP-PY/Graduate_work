from django.db import models
from django.conf import settings

class ImageFeed(models.Model):
    """
    Модель для хранения загруженных пользователями изображений и их обработанных версий.

    Attributes:
        user (ForeignKey): Пользователь, загрузивший изображение. Связан с моделью пользователя (AUTH_USER_MODEL).
        image (ImageField): Загруженное изображение.
        processed_image (ImageField, optional): Обработанное изображение. Может быть пустым или отсутствовать.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # user: Поле `ForeignKey` связывает `ImageFeed` с моделью пользователя (AUTH_USER_MODEL),
    # указывая, какой пользователь загрузил изображение. `on_delete=models.CASCADE` означает, что если пользователь
    # будет удален, то все связанные с ним записи в `ImageFeed` тоже будут удалены.

    image = models.ImageField(upload_to='images/')
    # image: Поле `ImageField` для хранения загруженного изображения. Атрибут `upload_to='images/'` указывает,
    # что файлы будут сохраняться в папке images/.

    processed_image = models.ImageField(upload_to='processed_images/', null=True, blank=True)
    # processed_image: Поле `ImageField` для хранения обработанной версии загруженного изображения.
    # Может быть пустым (null=True, blank=True). Файлы сохраняются в папке `processed_images/`.

    def __str__(self):
        """Возвращает строковое представление объекта"""
        # Метод `__str__`: Возвращает строку, содержащую имя пользователя и имя файла изображения.

        return f"{self.user.username} - {self.image.name}"

    def delete(self, *args, **kwargs):
        """
        Удаляет изображение и его обработанную версию перед удалением записи из базы данных.

        Args:
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.
        """
        # Метод `delete`: Переопределяет метод удаления, чтобы удалить файлы изображений с диска перед удалением записи из базы данных

        self.image.delete(save=False)
        if self.processed_image:
            self.processed_image.delete(save=False)
        super().delete(*args, **kwargs)

class DetectedObject(models.Model):
    """
    Модель для хранения данных об объектах, обнаруженных на изображениях.

    Attributes:
        image_feed (ForeignKey): Ссылка на связанное изображение из модели ImageFeed.
        object_type (CharField): Тип обнаруженного объекта.
        confidence (FloatField): Уверенность в обнаружении объекта (в диапазоне от 0 до 1).
        location (CharField): Местоположение обнаруженного объекта на изображении.
    """
    image_feed = models.ForeignKey(ImageFeed, related_name='detected_objects', on_delete=models.CASCADE)
    # image_feed: Поле `ForeignKey` связывает `DetectedObject` с `ImageFeed`.
    # `related_name='detected_objects'` позволяет получить все обнаруженные объекты для конкретного ImageFeed
    # с использованием `image_feed.detected_objects`.

    object_type = models.CharField(max_length=100)
    # object_type: Поле `CharField` для хранения типа обнаруженного объекта (например, "cat", "dog").

    confidence = models.FloatField()
    # confidence: Поле `FloatField` для хранения уровня уверенности в обнаружении объекта (в диапазоне от 0 до 1).

    location = models.CharField(max_length=255)
    # location: Поле `CharField` для хранения местоположения объекта на изображении в виде строки.

    def __str__(self):
        """Возвращает строковое представление объекта."""
        # __str__: Возвращает строку, содержащую тип объекта, уровень уверенности и имя файла изображения,
        # на котором обнаружен объект.
        return f"{self.object_type} ({self.confidence * 100}%) on {self.image_feed.image.name}"
