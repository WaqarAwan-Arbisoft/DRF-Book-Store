"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import PasswordRecovery, User


class UserAdmin(BaseUserAdmin):
    """Defining the admin page for the user"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('name',)}),
        ('Permissions', {
         'fields': ('is_active', 'is_staff', 'is_superuser', )}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(PasswordRecovery)
