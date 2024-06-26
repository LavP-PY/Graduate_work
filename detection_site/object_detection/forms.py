# Модуль forms.py в Django отвечает за создание и определение форм,
# которые используются для взаимодействия с данными веб-приложения. Он позволяет определять поля формы, их типы,
# валидацию данных и другие атрибуты, необходимые для сбора информации от пользователей.

from django import forms
from .models import ImageFeed
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm


class ImageFeedForm(forms.ModelForm):
    """
    Форма для загрузки изображений в модель ImageFeed.

    Attributes:
        Meta.model: Связанная модель ImageFeed.
        Meta.fields: Поля формы, включая только 'image'.
        Meta.widgets: Настройки виджета для поля 'image', ограничивающего загрузку изображений.
        Meta.help_texts: Подсказка для поля 'image' о загрузке изображения.
    """
    class Meta:
        """
        `class Meta` в Django используется для предоставления метаданных модели формы.

        Как это работает?
        - Когда мы используем форму ImageFeedForm в вашем представлении Django, она автоматически создает HTML-форму,
        которая отображает поле для загрузки изображений.
        - Виджет FileInput определяет, как будет выглядеть элемент интерфейса загрузки файла на стороне клиента.
        В данном случае, атрибут accept гарантирует, что пользователь может загружать только файлы изображений.
        - help_texts предоставляет пользователю пояснения о том, что ожидается от каждого поля формы.
        """
        model = ImageFeed
        # Определяем модель, с которой связана эта форма. Форма ImageFeedForm используется для работы с моделью ImageFeed.

        fields = ['image']
        # Указываем поля модели, которые должны быть включены в форму.
        # В данном случае, в форме будет только одно поле image, которое соответствует полю image в модели ImageFeed

        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        # атрибут `widgets = {...}` позволяет настроить виджеты для каждого поля формы.
        # В нашем коде для поля `image` задан виджет `FileInput` с атрибутом `accept`,
        # который ограничивает тип загружаемых файлов до изображений `(image/*)`.

        help_texts = {
            'image': 'Upload an image file.',
        }
        # `help_texts = {...}` Здесь задаются тексты с подсказками для каждого поля формы. В нашем случае,
        # для поля `image` задан текст "Upload an image file.", который будет отображаться рядом с полем в интерфейсе.


class UserSetNewPasswordForm(SetPasswordForm):
    """Изменение пароля пользователя после подтверждения"""
    def __init__(self, *args, **kwargs):
        """Обновление стилей формы"""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

class UserForgotPasswordForm(PasswordResetForm):
    """Запрос на восстановление пароля"""
    def __init__(self, *args, **kwargs):
        """Обновление стилей формы"""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })
