"""
Views for the User API
"""

from rest_framework import generics, authentication, permissions, exceptions

from user.models import User
from .serializers import NewUserSerializer, UserCodeSerializer, AuthTokenSerializer, UpdateUserSerializer, AdminUseUserSerializer, UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class ConfirmEmailView(generics.CreateAPIView):
    """Create a temporary user"""
    serializer_class = NewUserSerializer


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
    http_method_names = ['patch']

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class ListAllView(generics.ListAPIView):
    """List all users(Admin only)"""
    serializer_class = AdminUseUserSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]


class GetUserData(generics.RetrieveAPIView):
    """User can obtain its own data"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        userData = None

        try:
            userData = self.queryset.get(pk=self.request.user.pk)
        except:
            raise exceptions.ValidationError({"detail": "Unable to find user"})
        return userData
