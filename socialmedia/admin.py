"""
Admin module for the Social Media App
"""

from django.contrib import admin

from socialmedia.models import Friendship

# Register your models here.

admin.site.register(Friendship)
