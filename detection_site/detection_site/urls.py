"""
URL configuration for detection_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
# from detection_site.object_detection.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete


urlpatterns = [
    path('admin/', admin.site.urls),
    path('object_detection/', include('object_detection.urls')),
    path('', RedirectView.as_view(url='/object_detection/', permanent=True)),
    # path('password-reset/', password_reset, name='password_reset'),
    # path('password-reset/done/', password_reset_done, name='password_reset_done'),
    #
    # path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    # # path('password_reset_confirm/', password_reset_confirm, name='password_reset_confirm'),
    #
    # path('reset/done/', password_reset_complete, name='password_reset_complete')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
