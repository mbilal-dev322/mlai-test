from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import EmailVerificationToken, User


def send_verification_email(user: User):
    token = EmailVerificationToken.objects.create(user=user)
    link = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"
    send_mail(
        "Verify your email",
        f"Hi {user.username},\n\n"
        f"Your verification token (copy the whole line):\n{token.token}\n\n"
        f"Or click the link:\n{link}\n\n"
        "The token is valid for 24 hours.",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )


def send_password_reset_email(user: User):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
    send_mail(
        "Reset your password",
        f"Hi {user.username},\n\n"
        f"Your reset uid (copy the whole line):\n{uid}\n\n"
        f"Your reset token (copy the whole line):\n{token}\n\n"
        f"Or click the link:\n{link}\n\n"
        "The token expires in 15 minutes.",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
