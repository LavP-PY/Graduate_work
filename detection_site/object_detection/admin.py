from django.contrib import admin
from .models import ImageFeed, DetectedObject

# Регистрация моделей для отображения в административной панели Django
admin.site.register(ImageFeed)
admin.site.register(DetectedObject)
