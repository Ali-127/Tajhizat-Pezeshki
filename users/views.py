import random
from datetime import timedelta

from django.contrib.auth import get_user_model, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import OTPToken

User = get_user_model()


@ensure_csrf_cookie
@ensure_csrf_cookie
def auth_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'login.html')


def send_otp_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'invalid_method'}, status=405)

    phone_number = request.POST.get('phone_number', '').strip()
    full_name = request.POST.get('full_name', '').strip()
    mode = request.POST.get('mode', 'login')

    if not phone_number.isdigit() or len(phone_number) != 11:
        return JsonResponse({'error': 'invalid_phone'}, status=400)

    if mode == 'register' and not full_name:
        return JsonResponse({'error': 'invalid_name'}, status=400)

    if mode == 'login':
        if not User.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({
                'error': 'unregistered',
                'message': 'این شماره ثبت نشده است. لطفاً ابتدا در تب ثبت نام حساب کاربری ایجاد کنید.',
            }, status=400)

    otp_code = '{:06d}'.format(random.randint(0, 999999))
    OTPToken.objects.filter(phone_number=phone_number).delete()
    OTPToken.objects.create(phone_number=phone_number, otp_code=otp_code)

    print(f"[OTP DEBUG] phone={phone_number} otp={otp_code}")

    if mode == 'register':
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'full_name': full_name,
                'email': f'{phone_number}@example.com',
            },
        )
        if not created and user.full_name != full_name:
            user.full_name = full_name
            user.save(update_fields=['full_name'])

    return JsonResponse({'success': True})


def verify_otp_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'invalid_method'}, status=405)

    phone_number = request.POST.get('phone_number', '').strip()
    otp_code = request.POST.get('otp_code', '').strip()

    if not phone_number or not otp_code:
        return JsonResponse({'error': 'missing_fields'}, status=400)

    token = OTPToken.objects.filter(phone_number=phone_number, otp_code=otp_code).order_by('-created_at').first()
    if not token or timezone.now() - token.created_at > timedelta(minutes=10):
        return JsonResponse({'error': 'invalid_otp'}, status=400)

    user, _ = User.objects.get_or_create(
        phone_number=phone_number,
        defaults={
            'full_name': 'کاربر جدید',
            'email': f'{phone_number}@example.com',
        },
    )
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    OTPToken.objects.filter(phone_number=phone_number).delete()

    return JsonResponse({'success': True})


def logout_view(request):
    logout(request)
    return redirect('landing')


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('auth')
    return render(request, 'profile.html')
