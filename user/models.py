"""
User model file
"""
from email.policy import default
import pyotp

from django.contrib.auth.models import (AbstractBaseUser,
                                        PermissionsMixin,
                                        BaseUserManager)
from django.db import models


class UserManager(BaseUserManager):
    """User Model Manager"""

    def create_user(self, email,
                    password=None, **extraFields):
        """Create and return a new user"""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email),
                          **extraFields
                          )
        user.set_password(password)
        user.tempUser = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email,
                         password):
        """Create and return a new superuser"""
        user = self.create_user(
            email, password,
            user_code=pyotp.TOTP('base32secret3232').now()
        )
        user.is_staff = True
        user.is_superuser = True
        user.name = 'admin'
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=False,
                            default="Default username"
                            )
    image = models.ImageField(
        upload_to='images',
        null=True
    )
    age = models.IntegerField(default=18)
    country = models.CharField(max_length=50, default='Pakistan')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    creation = models.DateTimeField(auto_now_add=True)
    user_code = models.IntegerField(blank=True, null=True)
    tempUser = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class PasswordRecovery(models.Model):
    """Password Recovery Model"""
    email = models.EmailField(max_length=255)
    user_token = models.TextField(default='')
