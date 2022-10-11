"""
Serializers for the User API View
"""
from django.utils import timezone
from datetime import timedelta, datetime

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers, exceptions, status

from .models import PasswordRecovery
from .utils import UserAppBusinessLogic


class NewUserSerializer(serializers.ModelSerializer):
    """
    Serializer for a temporary user
    """
    class Meta:
        model = get_user_model()
        fields = [
            'email', 'password', 'name',
            'image', 'country', 'age'
        ]

    def run_validation(self, data=...):
        get_user_model().objects.filter(
            creation__lt=datetime.now()
            - timedelta(minutes=3),
            tempUser=True
        ).delete()
        return super().run_validation(data)

    def validate_password(self, value):
        if len(value) < 5:
            raise exceptions.ValidationError(
                detail='Password should be at least 5 characters long.')

    def create(self, validated_data):
        """
        Sending email and perform the user creation in the system
        """
        if get_user_model().objects.filter(email=validated_data['email']):
            raise exceptions.ValidationError(
                'Another user with this email already exists.'
            )
        code = UserAppBusinessLogic().send_mail(email=validated_data['email'])
        return get_user_model().objects.create_user(**validated_data, user_code=code)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user class"""
    class Meta:
        model = get_user_model()
        fields = [
            'id', 'email', 'name',
            'image', 'country', 'age',
            'is_staff'
        ]


class UserSerializerPublic(serializers.ModelSerializer):
    """Serializer for the user class"""
    class Meta:
        model = get_user_model()
        fields = [
            'id', 'email', 'name',
            'image', 'country', 'age'
        ]


class UserCodeSerializer(serializers.ModelSerializer):
    """Serializer for user Code"""
    class Meta:
        model = get_user_model()
        fields = ['user_code']

    def update(self, instance, validated_data):
        """Create a new user in the system"""
        if (timezone.now() >
                (instance.creation+timedelta(minutes=3)) and instance.tempUser):
            instance.delete()
            raise exceptions.ValidationError(
                'Your verification code has been expired. Please try again!'
            )
        instance.tempUser = False
        instance.user_code = -1*instance.user_code
        instance.save()
        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    """Serializer for update user"""

    class Meta:
        model = get_user_model()
        fields = [
            'password', 'name',
            'image', 'country',
            'age'
        ]


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = get_user_model().objects.get(email=email, password=password)
        except:
            user = None
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            raise Exception("sdfdsf")
        attrs['user'] = user
        return attrs


class UserCommentSerializer(serializers.ModelSerializer):
    """Serializer to be used to display comment"""
    class Meta:
        model = get_user_model()
        fields = [
            'id', 'name',
            'image', 'country'
        ]


class SetUpdatePasswordTokenSerializer(serializers.ModelSerializer):
    """Serializer to update the user password"""
    class Meta:
        model = PasswordRecovery
        fields = ['email']

    def create(self, validated_data):
        """Create and send link to the user"""
        if not get_user_model().objects.filter(email=validated_data['email']):
            raise exceptions.ValidationError(
                'No User exists in the system with this email.'
            )
        if PasswordRecovery.objects.filter(email=validated_data['email']):
            raise exceptions.ValidationError(
                'A recovery email has already been sent to you.'
            )

        token = UserAppBusinessLogic().send_recovery_link(
            validated_data['email']
        )
        return PasswordRecovery.objects.create(
            email=validated_data['email'], user_token=token)


class RetrieveTokenSerializer(serializers.ModelSerializer):
    """Serializer to destroy available link"""
    class Meta:
        model = PasswordRecovery
        fields = ['email', 'user_token']


class UpdatePasswordSerializer(serializers.ModelSerializer):
    """Serializer for updating user password"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

    def update(self, instance, validated_data):
        PasswordRecovery.objects.filter(
            email=validated_data['email']).delete()
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
