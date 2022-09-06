"""
User model file
"""

import random
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator


class UserManager(BaseUserManager):
    """User Model Manager"""

    def create_user(self, email, password=None, **extraFields):
        """Create and return a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extraFields)
        user.set_password(password)
        user.save(using=self._db)
        if extraFields.get('user_code'):
            TempUser.objects.filter(
                user_code=extraFields['user_code']).delete()
        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(
        max_length=255, blank=False)
    image = models.ImageField(upload_to="images")
    age = models.IntegerField(validators=[MinValueValidator(15)], default=18)
    country = models.CharField(max_length=50, default='Pakistan')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    creation = models.DateTimeField(auto_now_add=True)
    user_code = models.IntegerField(blank=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class TempUser(models.Model):
    """Temporary user in the system"""
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=20, validators=[
                                MinLengthValidator(5)])
    name = models.CharField(max_length=255, blank=False)
    image = models.ImageField(
        upload_to="images", default="images/DEFAULT_PROFILE_IMAGE_BACKEND_UPLOADED.png")
    age = models.IntegerField(validators=[MinValueValidator(15)], default=18)
    country = models.CharField(max_length=50, default='Pakistan')
    creation = models.DateTimeField(auto_now_add=True)
    user_code = models.IntegerField(
        default=random.randint(100000, 999999), unique=True, null=True, blank=True)
