from django.urls import path

from .views import auth_view, send_otp_view, verify_otp_view, logout_view

urlpatterns = [
    path('auth/', auth_view, name='auth'),
    path('auth/send-otp/', send_otp_view, name='send_otp'),
    path('auth/verify-otp/', verify_otp_view, name='verify_otp'),
    path('logout/', logout_view, name='logout'),
]
