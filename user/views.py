"""
Views for the User API
"""

from rest_framework import generics, authentication, permissions, exceptions

from user.models import User
from .serializers import TempUserSerializer, UserCodeSerializer, AuthTokenSerializer, UpdateUserSerializer, AdminUseUserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.core import mail
import pyotp


class ConfirmEmailView(generics.CreateAPIView):
    """Create a temporary user"""
    serializer_class = TempUserSerializer

    def perform_create(self, serializer):
        """Sending email and perform the user creation in the system"""
        if User.objects.filter(email=serializer.validated_data['email']):
            raise exceptions.ValidationError(
                "Another user with this email already exists.", code='email')
        totp = pyotp.TOTP('base32secret3232')
        code = totp.now()
        with mail.get_connection() as connection:
            mail.EmailMessage(
                "Email Verification", f"<h1>${code}</h1>", "the-book-spot@admin.com", [
                    serializer.validated_data['email']],
                connection=connection,
            ).send()
        serializer.save(user_code=code)


class CompleteRegistration(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserCodeSerializer


class CreateTokenView(ObtainAuthToken):
    """Create an auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UpdateUserView(generics.UpdateAPIView):
    """Update the existing user"""
    serializer_class = UpdateUserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class ListAllView(generics.ListAPIView):
    """List all users(Admin only)"""
    serializer_class = AdminUseUserSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
