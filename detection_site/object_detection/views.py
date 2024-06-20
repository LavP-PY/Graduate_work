from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .models import ImageFeed, DetectedObject
from .utils import process_image, process_alternative_image
from .forms import ImageFeedForm, UserForgotPasswordForm, UserSetNewPasswordForm
from .tasks import process_image_task

from django.http import HttpResponseBadRequest


def home(request):
    """Отображает главную страницу"""
    return render(request, 'object_detection/home.html')


def register(request):
    """
    Обрабатывает регистрацию нового пользователя.

    :param request: HTTP запрос.
    :type request: HttpRequest
    :return: HTTP ответ с формой регистрации.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('object_detection:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'object_detection/register.html', {'form': form})


def user_login(request):
    """
    Обрабатывает аутентификацию пользователя.

    :param request: HTTP запрос.
    :type request: HttpRequest
    :return: HTTP ответ с формой аутентификации.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('object_detection:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'object_detection/login.html', {'form': form})


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """Обрабатывает запрос на восстановление пароля по электронной почте"""
    form_class = UserForgotPasswordForm
    template_name = 'object_detection/password_reset_form.html'
    # success_url = reverse_lazy('home')
    success_url = reverse_lazy('object_detection:password_reset_done')
    success_message = 'Письмо с инструкцией по восстановлению пароля отправлено на ваш email'
    subject_template_name = 'object_detection/email/password_subject_reset_email.txt'
    email_template_name = 'object_detection/email/password_reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Запрос на восстановление пароля'
        return context

class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """Обрабатывает установку нового пароля после подтверждения запроса на восстановление"""
    form_class = UserSetNewPasswordForm
    template_name = 'object_detection/password_reset_confirm.html'
    # success_url = reverse_lazy('home')
    success_url = reverse_lazy('object_detection:password_reset_complete')
    success_message = 'Пароль успешно изменён. Можете авторизоваться на сайте.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установить новый пароль'
        return context

def password_reset_done(request):
    """Отображает страницу подтверждения отправки письма с инструкцией по восстановлению пароля"""
    return render(request, 'object_detection/password_reset_done.html')

def password_reset_complete(request):
    """Отображает страницу подтверждения успешного изменения пароля"""
    return render(request, 'object_detection/password_reset_complete.html')


@login_required
def user_logout(request):
    """Обрабатывает выход пользователя из системы"""
    logout(request)
    return redirect('object_detection:login')


@login_required
def dashboard(request):
    """
    Отображает панель управления пользователя с загруженными изображениями.

    :param request: HTTP запрос.
    :type request: HttpRequest
    :return: HTTP ответ с панелью управления.
    :rtype: HttpResponse
    """
    # image_feeds = ImageFeed.objects.filter(user=request.user)
    image_feeds = ImageFeed.objects.all()
    context = {'image_feeds': image_feeds}
    return render(request, 'object_detection/dashboard.html', context)


@login_required
def process_image_feed(request, feed_id):
    """
    Функция выполняет следующие действия:
    - проверяет, что пользователь авторизован (с помощью декоратора @login_required);
    - получает объект `ImageFeed` с указанным `feed_id` для текущего пользователя;
    - вызывает функцию `process_image` для обработки изображения.
    - перенаправляет пользователя обратно на страницу `dashboard`
    Функция `process_image` определяется в `utils.py` и выполняет основную работу по обработке изображения.

    Улучшения:
    1. Асинхронная обработка: Обработка изображений может быть ресурсоемкой и занимать время. Рассмотрим возможность
    асинхронной обработки изображений, например, с использованием библиотеки Celery для выполнения задач в фоновом режиме
    2. Логирование и обработка ошибок: Добавим логирование и обработку ошибок в функции process_image_feed и
    process_image для лучшего отслеживания и обработки исключительных ситуаций.


    :param request: HTTP запрос.
    :type request: HttpRequest
    :param feed_id: Идентификатор записи ImageFeed, содержащей изображение для обработки.
    :type feed_id: int
    :return: HTTP ответ с перенаправлением на панель управления.
    :rtype: HttpResponse
    """
    image_feed = get_object_or_404(ImageFeed, id=feed_id, user=request.user)
    process_image(feed_id)
    # process_image_task.delay(feed_id)
    messages.success(request, 'Изображение отправлено на обработку. Пожалуйста, подождите.')
    return redirect('object_detection:dashboard')


@login_required
def process_alter_image_feed(request, feed_id):
    """
    Обрабатывает изображение с использованием альтернативной модели и сохраняет результаты.

    :param request: HTTP запрос.
    :type request: HttpRequest
    :param feed_id: Идентификатор записи ImageFeed, содержащей изображение для обработки.
    :type feed_id: int
    :return: HTTP ответ с перенаправлением на панель управления.
    :rtype: HttpResponse
    """
    image_feed = get_object_or_404(ImageFeed, id=feed_id, user=request.user)
    if process_alternative_image(feed_id):
        messages.success(request, 'Изображение успешно обработано альтернативной моделью.')
    else:
        messages.error(request, 'Ошибка обработки изображения альтернативной моделью.')
    return redirect('object_detection:dashboard')


@login_required
def upload_image(request): # бывшая add_image_feed()
    """
    Отображает форму загрузки изображения и обрабатывает загруженное изображение..

    :param request: HTTP запрос.
    :type request: HttpRequest
    :return: HTTP ответ с формой загрузки или перенаправление на страницу панели управления.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = ImageFeedForm(request.POST, request.FILES)
        if form.is_valid():
            image_feed = form.save(commit=False)
            image_feed.user = request.user
            image_feed.save()

            if 'process_image' in request.POST:
                # if 'process_image' in request.POST:
                #     process_image(image_feed.id)
                #     messages.success(request, 'Изображение успешно обработано.')
                if process_image(image_feed.id):
                    messages.success(request, 'Изображение успешно обработано.')
                else:
                    messages.error(request, 'Ошибка обработки изображения.')
            elif 'process_alternative_image' in request.POST:
                detections = process_alternative_image(image_feed.id)
                if detections:
                    # Сохранение результатов в базу данных (если нужно)
                    for detection in detections:
                        DetectedObject.objects.create(
                            image_feed=image_feed,
                            object_type=detection['label'],
                            location=f"{detection['box'][0]},{detection['box'][1]},{detection['box'][2]},{detection['box'][3]}",
                            confidence=float(detection['score'])
                        )
                    messages.success(request, 'Изображение успешно обработано альтернативной моделью.')
                else:
                    messages.error(request, 'Ошибка обработки изображения альтернативной моделью.')

            return redirect('object_detection:dashboard')
    else:
        form = ImageFeedForm()
    return render(request, 'object_detection/add_image_feed.html', {'form': form})

@login_required
def delete_image(request, image_id):
    """
    Удаляет изображение и связанные с ним данные из базы данных, при удалении их на сайте.

    :param request: HTTP запрос.
    :type request: HttpRequest
    :param image_id: Идентификатор изображения для удаления.
    :type image_id: int
    :return: HTTP ответ с перенаправлением на панель управления.
    :rtype: HttpResponse
    """
    image = get_object_or_404(ImageFeed, id=image_id, user=request.user)  # Ensuring only the owner can delete
    # image.image.delete()
    # if image.processed_image:
    #     image.processed_image.delete()
    image.delete()
    messages.success(request, 'Изображение успешно удалено.')
    return redirect('object_detection:dashboard')


def about(request):
    """
    Отображает страницу с информацией о сайте.

    :param request: HTTP запрос.
    :type request: HttpRequest
    :return: HTTP ответ с информацией о сайте.
    :rtype: HttpResponse
    """
    return render(request, 'object_detection/about.html')
