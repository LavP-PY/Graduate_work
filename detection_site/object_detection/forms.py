from django import forms
from .models import ImageFeed
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm




class ImageFeedForm(forms.ModelForm):
    class Meta:
        model = ImageFeed
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        help_texts = {
            'image': 'Upload an image file.',
        }

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