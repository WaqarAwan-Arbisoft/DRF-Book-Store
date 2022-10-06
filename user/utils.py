"""
This module defines the business logics for User app
"""
import pyotp
import secrets

from django.core import mail

from bookshop.settings import env


class UserAppBusinessLogic():
    """Defines the business login for User App"""

    def send_mail(email):
        """Send the email to the user"""
        totp = pyotp.TOTP('base32secret3232')
        code = totp.now()
        with mail.get_connection() as connection:
            mail.EmailMessage(
                'Email Verification', f'<h1>Your verification code for registration is: ${code}</h1>', env(
                    'ADMIN_EMAIL'), [email],
                connection=connection
            ).send()
        return code

    def send_recovery_link(email):
        """Send a recovery link to the email"""
        token = secrets.token_hex(16)
        with mail.get_connection() as connection:
            mail.EmailMessage(
                'Email Verification', f"<a href='{env('FRONTEND_DOMAIN')+'/recover/'+token}' target='_blank'>Recover Account</a>", 'the-book-spot@admin.com',
                [email], connection=connection,
            ).send()
        return token
