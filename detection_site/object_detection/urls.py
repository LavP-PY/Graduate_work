"""
Конфигурация URL для приложения object_detection.

Этот модуль содержит шаблоны URL для приложения object_detection.
Он связывает URL маршруты с соответствующими представлениями.

Маршруты:
    - Главная страница
    - Страница "О нас"
    - Регистрация пользователя
    - Вход пользователя
    - Выход пользователя
    - Панель управления пользователя
    - Обработка потока изображений
    - Загрузка потока изображений
    - Удаление изображения
    - Альтернативная обработка потока изображений
    - Маршруты для сброса пароля

Статические медиафайлы также обслуживаются в режиме разработки.
"""

from django.urls import path
from .views import (
    home, register, user_login, user_logout, dashboard, process_image_feed,
    upload_image, delete_image, UserForgotPasswordView, UserPasswordResetConfirmView,
    password_reset_done, password_reset_complete, process_alter_image_feed, about
)
from django.conf import settings
from django.conf.urls.static import static
from typing import List

app_name = 'object_detection'

# Определение шаблонов URL для приложения object_detection
urlpatterns: List[path] = [
    # Главная страница
    path('', home, name='home'),
    # Страница "О нас"
    path('about/', about, name='about'),
    # Регистрация пользователя
    path('register/', register, name='register'),
    # Вход пользователя
    path('login/', user_login, name='login'),
    # Выход пользователя
    path('logout/', user_logout, name='logout'),
    # Панель управления пользователя
    path('dashboard/', dashboard, name='dashboard'),
    # Обработка потока изображений
    path('process/<int:feed_id>/', process_image_feed, name='process_feed'),
    # Загрузка потока изображений
    path('add-image-feed/', upload_image, name='add_image_feed'),
    # Удаление изображения
    path('image/delete/<int:image_id>/', delete_image, name='delete_image'),
    # Альтернативная обработка потока изображений
    path('process-alternative/<int:feed_id>/', process_alter_image_feed, name='process_alternative'),
    # Маршруты для сброса пароля
    path('password-reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('password-reset/done/', password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', password_reset_complete, name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Описание модуля `urls.py`:
# Модуль `urls.py` определяет маршруты URL для приложения Django.
#
# 1. Импорт модулей:
#     - `path` из `django.urls`: Используется для определения маршрутов URL.
#     - Импорт представлений из `views`: Все представления, которые будут связаны с маршрутами
#     - `settings` из `django.conf`: Используется для получения настроек проекта
#     - `static` из `django.conf.urls.static`: Используется для обслуживания медиафайлов в режиме разработки
#
# 2. Определение `app_name = 'object_detection'`: Устанавливает пространство имен для этого набора маршрутов,
# что позволяет ссылаться на URL этого приложения из других частей проекта.
#
# 3. Определение `urlpatterns`: Это список маршрутов URL, которые связывают URL с соответствующими представлениями.
#
# 4. Маршруты:
#     - Каждый path определяет URL и связывает его с представлением;
#     - Используются как обычные представления (например, home, about, register),
#     так и классовые представления (например, UserForgotPasswordView).
# 5. Добавление маршрутов для медиафайлов: в режиме разработки добавляются маршруты для обслуживания медиафайлов.
