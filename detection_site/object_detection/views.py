from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import ImageFeed
from .utils import process_image
from .forms import ImageFeedForm


def home(request):
    return render(request, 'object_detection/home.html')


def register(request):
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
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('object_detection:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'object_detection/login.html', {'form': form})


# def password_reset(request):
#     if request.method == 'POST':
#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             user = get_user_model().objects.get(email=email)
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             url = request.build_absolute_uri(reverse('object_detection:password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
#             message = render_to_string('registration/password_reset_email.html', {
#                 'user': user,
#                 'url': url,
#             })
#             send_mail('Password Reset', message, settings.DEFAULT_FROM_EMAIL, [user.email])
#             return redirect('object_detection:password_reset_done')
#     else:
#         form = PasswordResetForm()
#     return render(request, 'registration/password_reset_form.html', {'form': form})

# def password_reset(request):
#     if request.method == 'POST':
#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             user = get_user_model().objects.get(email=email)
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             domain = request.get_host()
#             protocol = 'https' if request.is_secure() else 'http'
#             message = render_to_string('registration/password_reset_email.html', {
#                 'user': user,
#                 'domain': domain,
#                 'protocol': protocol,
#                 'uid': uid,
#                 'token': token,
#             })
#             send_mail('Password Reset', message, settings.DEFAULT_FROM_EMAIL, [user.email])
#             return redirect('object_detection:password_reset_done')
#     else:
#         form = PasswordResetForm()
#     return render(request, 'registration/password_reset_form.html', {'form': form})

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_user_model().objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
            print(f'Domain: {domain}, Protocol: {protocol}, UID: {uid}, Token: {token}')  # Логирование
            message = render_to_string('registration/password_reset_email.html', {
                'user': user,
                'domain': domain,
                'protocol': protocol,
                'uid': uid,
                'token': token,
            })
            send_mail('Password Reset', message, settings.DEFAULT_FROM_EMAIL, [user.email])
            return redirect('object_detection:password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})


def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')

# def password_reset_confirm(request, uidb64, token):
#     uid = force_str(urlsafe_base64_decode(uidb64))
#     user = get_user_model().objects.get(pk=uid)
#     if default_token_generator.check_token(user, token):
#         if request.method == 'POST':
#             form = SetPasswordForm(user, request.POST)
#             if form.is_valid():
#                 form.save()
#                 return redirect('object_detection:password_reset_complete')
#         else:
#             form = SetPasswordForm(user)
#         return render(request, 'registration/password_reset_confirm.html', {'form': form})
#     else:
#         return redirect('object_detection:password_reset_done')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('object_detection:password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        print(f'Invalid link. UID: {uidb64}, Token: {token}')  # Логирование
        return redirect('object_detection:password_reset_done')


def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('object_detection:login')


@login_required
def dashboard(request):
    image_feeds = ImageFeed.objects.filter(user=request.user)
    return render(request, 'object_detection/dashboard.html', {'image_feeds': image_feeds})


@login_required
def process_image_feed(request, feed_id):
    image_feed = get_object_or_404(ImageFeed, id=feed_id, user=request.user)
    process_image(feed_id)  # Consider handling this asynchronously
    return redirect('object_detection:dashboard')


@login_required
def add_image_feed(request):
    if request.method == 'POST':
        form = ImageFeedForm(request.POST, request.FILES)
        if form.is_valid():
            image_feed = form.save(commit=False)
            image_feed.user = request.user
            image_feed.save()
            return redirect('object_detection:dashboard')
    else:
        form = ImageFeedForm()
    return render(request, 'object_detection/add_image_feed.html', {'form': form})

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ImageFeed, id=image_id, user=request.user)  # Ensuring only the owner can delete
    # image.image.delete()
    # if image.processed_image:
    #     image.processed_image.delete()
    image.delete()
    return redirect('object_detection:dashboard')


