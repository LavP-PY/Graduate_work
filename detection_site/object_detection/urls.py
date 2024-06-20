from django.urls import path
from .views import (home, register, user_login, user_logout, dashboard, process_image_feed,
                    upload_image, delete_image, UserForgotPasswordView, UserPasswordResetConfirmView,
                    password_reset_done, password_reset_complete, process_alter_image_feed, about)
from django.conf import settings
from django.conf.urls.static import static

app_name = 'object_detection'

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('process/<int:feed_id>/', process_image_feed, name='process_feed'),
    path('add-image-feed/', upload_image, name='add_image_feed'),
    path('image/delete/<int:image_id>/', delete_image, name='delete_image'),

    path('process-alternative/<int:feed_id>/', process_alter_image_feed, name='process_alternative'),

    path('password-reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('password-reset/done/', password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', password_reset_complete, name='password_reset_complete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
