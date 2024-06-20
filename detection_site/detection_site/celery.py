from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем модуль настроек Django для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'detection_site.settings')

app = Celery('detection_site')

# Используем строку для конфигурации Celery, а не сериализатор json.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находит асинхронные задачи в приложениях Django.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
