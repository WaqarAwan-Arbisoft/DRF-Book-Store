"""
Serializers for the User API View
"""
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from .models import User, UserCode
from datetime import timedelta


class NewUserSerializer(serializers.ModelSerializer):
    """Serializer for a temporary user"""
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'image', 'country', 'age']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user class"""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'image', 'country', 'age', 'is_staff']


class UserCodeSerializer(serializers.ModelSerializer):
    """Serializer for user Code"""
    class Meta:
        model = UserCode
        fields = '__all__'

    def create(self, validated_data):
        """Create a new user in the system"""

        tempUser = None
        try:
            tempUser = User.objects.get(
                user_code=validated_data['user_code'])
        except:
            raise serializers.ValidationError(
                {"detail": "Invalid OTP entered."})
        if timezone.now() > (tempUser.creation+timedelta(minutes=3)):
            tempUser.delete()
            raise serializers.ValidationError(
                {"detail": "Your verification code has been expired. Please try again!"})
        tempUser.delete()
        tempUser.tempUser = False
        tempUser.user_code = ''
        tempUser.save()
        return super().create(validated_data)


class UpdateUserSerializer(serializers.ModelSerializer):
    """Serializer for update user"""

    class Meta:
        model = get_user_model()
        fields = ['password', 'name', 'image', 'country', 'age']

        def update(self, instance, validated_data):
            """Update and return an existing user"""
            password = validated_data.pop('password', None)
            user = super().update(instance, validated_data)
            if password:
                user.set_password(password)
                user.save()

            return user


class AdminUseUserSerializer(serializers.ModelSerializer):
    """Serializer to be used by admins"""
    class Meta:
        model = get_user_model()
        fields = ['email', 'name', 'image', 'country', 'age']


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

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            raise serializers.ValidationError(
                "Unable to authenticate with the provided credentials", code='authorization')
        attrs['user'] = user
        return attrs
