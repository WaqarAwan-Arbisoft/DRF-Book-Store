"""
Views for the User API
"""

from rest_framework import generics, authentication, permissions
from .serializers import UserSerializer
from .serializers import TempUserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import AuthTokenSerializer
from rest_framework.settings import api_settings
from django.core import mail
from .models import User
import random


class ConfirmEmailView(generics.CreateAPIView):
    """Create a temporary user"""
    serializer_class = TempUserSerializer

    def perform_create(self, serializer):
        """Sending email and perform the user creation in the system"""
        code = random.randint(100000, 999999)
        with mail.get_connection() as connection:
            mail.EmailMessage(
                "Email Verification", f"<h1>${code}</h1>", "the-book-spot@admin.com", [
                    serializer.validated_data['email']],
                connection=connection,
            ).send()
        serializer.save(user_code=code)


class CompleteRegistration(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create an auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
