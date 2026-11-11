import uuid

from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .emails import send_password_reset_email, send_verification_email
from .models import EmailVerificationToken, User
from .serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
    ResetPasswordConfirmSerializer,
    ResetPasswordRequestSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data.get("email"))
        except User.DoesNotExist:
            user = None
        if user and not user.is_verified:
            return Response(
                {"detail": "Email not verified. Request a new verification email."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data["refresh"]).blacklist()
        except KeyError:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"detail": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = EmailVerificationToken.objects.get(token=uuid.UUID(str(token)))
        except (EmailVerificationToken.DoesNotExist, ValueError):
            return Response({"detail": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)
        token.user.is_verified = True
        token.user.save(update_fields=["is_verified"])
        token.delete()
        return Response({"detail": "Email verified successfully."})


class ResendVerificationView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first() if email else None
        if user and not user.is_verified:
            send_verification_email(user)
        # Always 200 so accounts are not enumerable.
        return Response({"detail": "If the account exists and is unverified, a verification email was sent."})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        RefreshToken.for_user(user)  # rotating credentials after password change
        return Response({"detail": "Password changed. Please log in again."})


class ResetPasswordRequestView(APIView):
    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data["email"], is_active=True).first()
        if user:
            send_password_reset_email(user)
        return Response({"detail": "If the account exists, a password reset email was sent."})


class ResetPasswordConfirmView(APIView):
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset."})
