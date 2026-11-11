from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    ResendVerificationView,
    ResetPasswordConfirmView,
    ResetPasswordRequestView,
    VerifyEmailView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/verify-email/", VerifyEmailView.as_view()),
    path("auth/resend-verification/", ResendVerificationView.as_view()),
    path("auth/change-password/", ChangePasswordView.as_view()),
    path("auth/reset-password/", ResetPasswordRequestView.as_view()),
    path("auth/reset-password/confirm/", ResetPasswordConfirmView.as_view()),
]
