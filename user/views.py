"""
Views for the User API
"""
from rest_framework import generics, authentication, permissions, exceptions, pagination
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

from user.models import PasswordRecovery
from .serializers import (GoogleRegisterSerializer, NewUserSerializer,
                          RetrieveTokenSerializer, PasswordRecoverySerializer,
                          UpdatePasswordSerializer, UserCodeSerializer,
                          AuthTokenSerializer, UpdateUserSerializer,
                          UserSerializer,
                          )


class ConfirmEmailView(generics.CreateAPIView):
    """
    View for creating a temporary user and sending email 
    for confirmation.
    """
    serializer_class = NewUserSerializer


class CompleteRegistration(generics.UpdateAPIView):
    """Create a new user in the system"""
    serializer_class = UserCodeSerializer
    http_method_names = ['patch']

    def get_object(self):
        try:
            return get_user_model().objects.get(
                user_code=self.request.data['user_code'],
                tempUser=True
            )
        except:
            raise exceptions.ValidationError(
                'Invalid OTP entered.'
            )


class GoogleRegisterView(generics.CreateAPIView):
    """
    Register with google
    """
    serializer_class = GoogleRegisterSerializer


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
        return get_user_model().objects.get(id=self.request.user.id)

    def perform_update(self, serializer):
        password = serializer.validated_data.pop('password', None)
        super().perform_update(serializer)
        user = self.get_object()
        if password:
            user.set_password(password)
            user.save()
        return user


class ListAllView(generics.ListAPIView):
    """List all users"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'email']
    PAGE_SIZE = 5
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return get_user_model().objects.filter(is_staff=False)


class GetUserByIdView(generics.RetrieveAPIView):
    """User can obtain its own data"""
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get_object(self):
        user = None
        try:
            user = get_user_model().objects.get(id=self.kwargs.get('userId'))
        except:
            raise exceptions.ValidationError('Unable to find user')
        if (user.is_superuser or user.is_staff):
            raise exceptions.ValidationError('Unable to find user')
        return user


class GetUserData(generics.RetrieveAPIView):
    """User can obtain its own data"""
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        userData = None

        try:
            userData = self.queryset.get(pk=self.request.user.pk)
        except:
            raise exceptions.ValidationError('Unable to find user')
        return userData


class EmailRecoveryLink(generics.CreateAPIView):
    """Email recovery view to send link to the user"""
    serializer_class = PasswordRecoverySerializer


class CheckTokenAvailability(generics.RetrieveAPIView):
    """Check token availability and destroy if available"""
    serializer_class = RetrieveTokenSerializer

    def get_object(self):
        token = None
        try:
            token = PasswordRecovery.objects.get(
                user_token=self.kwargs.get('token'))
        except:
            raise exceptions.ValidationError('Invalid Token.')
        return token


class UpdateRecoveredPasswordView(generics.UpdateAPIView):
    """Update the password with the new password"""
    serializer_class = UpdatePasswordSerializer
    http_method_names = ['patch']

    def get_object(self):
        return get_user_model().objects.get(email=self.request.data['email'])
