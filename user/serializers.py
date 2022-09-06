"""
Serializers for the User API View
"""
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from .models import User
from .models import TempUser
from datetime import datetime, timedelta


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['user_code']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a new user"""
        tempUser = TempUser.objects.filter(
            user_code=validated_data['user_code'])
        if (len(tempUser) == 0):
            raise serializers.ValidationError(
                "Invalid user code.", code='authorization')
        if timezone.now() > (tempUser[0].creation+timedelta(minutes=3)):
            tempUser = TempUser.objects.filter(
                user_code=validated_data['user_code']).delete()
            raise serializers.ValidationError(
                "Your verification code has been expired. Please try again!")
        return get_user_model().objects.create_user(**tempUser.values()[0])


class UpdateUserSerializer(UserSerializer):
    """Serializer for update user"""
    class Meta(UserSerializer.Meta):
        fields = ['password', 'name', 'image', 'country', 'age']

        def update(self, instance, validated_data):
            """Update and return an existing user"""
            password = validated_data.pop('password', None)
            user = super().update(instance, validated_data)
            if password:
                user.set_password(password)
                user.save()

            return user


class TempUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempUser
        fields = ['email', 'password', 'name', 'image', 'country', 'age']


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
