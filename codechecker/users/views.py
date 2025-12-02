from users.tasks import send_verification_email
from rest_framework import generics, permissions
from users.serializers import RegisterSerializer
from users.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

from users.utils import email_verification_token


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = True
        user.save()

        token = email_verification_token.make_token(user)
        uid = user.id

        verification_url = (
            f"{settings.FRONTEND_URL}/verify-email.html?uid={uid}&token={token}"
        )

        send_verification_email.delay(user.email, verification_url)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email and password required"}, status=400)

        # Django authenticate() работает по username — если email=username, это ок
        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({"detail": "Invalid credentials"}, status=400)

        if not user.email_verified:
            return Response({"detail": "Email not verified"}, status=400)

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user_id": user.id,
            "email": user.email,
        })


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")

        try:
            user = User.objects.get(id=uid)
        except User.DoesNotExist:
            return Response({"detail": "Invalid user"}, status=400)

        if not email_verification_token.check_token(user, token):
            return Response({"detail": "Invalid or expired token"}, status=400)

        user.email_verified = True
        user.save()

        return Response({"detail": "Email verified successfully"})
