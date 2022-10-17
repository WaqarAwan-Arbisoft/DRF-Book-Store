"""
Test the User app features
"""

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.urls import reverse


class UserAppTests(APITestCase):
    """
    Tests for User Application
    """

    def register_temp_user(self, email):
        """
        Register a temp user
        """
        data = {
            'name': 'Test User',
            'email': email,
            'password': '123testing123'
        }
        url = reverse('confirm-email')
        return self.client.post(url, data, format='json')

    def create_user_and_set_token_credentials(self, email):
        """
        Create a new permanent user
        """
        data = {
            'name': 'Test User',
            'email': email,
            'password': '123testing123'
        }
        user = get_user_model().objects.create_user(
            email=data['email'], password=data['password'],
            name=data['name'], tempUser=False,
            user_code=123456
        )
        token = Token.objects.create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {0}'.format(token.key)
        )
        return user

    def create_user(self, email):
        """
        Create a user in the database
        """
        data = {
            'name': 'Test User',
            'email': email,
            'password': '123testing123'
        }
        user = get_user_model().objects.create_user(
            email=data['email'], password=data['password'],
            name=data['name'], tempUser=False,
            user_code=123456
        )
        return user

    def test_register_and_save_temp_user(self):
        """
        Ensure we can register the user with data 
        and save the user as a temporary user
        """
        user_email = 'test_user@gmail.com'
        response = self.register_temp_user(email=user_email)
        assert response.status_code == status.HTTP_201_CREATED
        assert get_user_model().objects.get().email == user_email
        assert get_user_model().objects.get().tempUser == True
        assert get_user_model().objects.count() == 1
        # User already exists
        user_email = 'test_user@gmail.com'
        response = self.register_temp_user(email=user_email)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_complete_registration(self):
        """
        Ensure that we can completely register the user
        by confirming their email.
        """
        user_email = 'test_user@gmail.com'
        self.register_temp_user(email=user_email)
        confirmation_code = {
            'user_code': get_user_model().objects.get().user_code,
        }
        url = reverse('register')
        response = self.client.patch(url, confirmation_code, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_update_profile(self):
        """
        Ensure that user will be allowed to update his/her own profile
        with authorization token.
        """
        user = self.create_user_and_set_token_credentials(
            email='test_user1@gmail.com'
        )
        assert get_user_model().objects.get().name == user.name
        updateData = {
            'name': 'Test User Updated'
        }
        url = reverse('update')
        response = self.client.patch(url, updateData, format='json')
        assert response.status_code == status.HTTP_200_OK
        """
        Clearing up credentials to check if the response is false for
        non-auth users
        """
        self.client.credentials()
        response = self.client.patch(url, updateData, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fetch_all_users(self):
        """
        Ensure that only the authenticated user will be able to
        fetch all the users
        """
        self.create_user_and_set_token_credentials(
            email='test_user1@gmail.com'
        )
        url = reverse('list-all')
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        """
        Clearing up credentials
        """
        self.client.credentials()
        response = self.client.patch(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fetch_profile_data(self):
        """
        Ensure that the user will be able to fetch his/her own data.
        """
        self.create_user_and_set_token_credentials(
            email='test_user1@gmail.com'
        )
        url = reverse('fetch-user-data')
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        """
        Clearing up credentials
        """
        self.client.credentials()
        response = self.client.patch(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fetch_profile_by_id(self):
        """
        Ensure that user's profile can be fetched by id
        """
        user = self.create_user(email='test_user1@gmail.com')
        url = reverse('fetch-user-by-id', kwargs={'userId': user.id})
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_password_recovery_email(self):
        """
        Ensure that the app sends the password recovery mail
        """
        user = self.create_user(email='test_user1@gmail.com')
        url = reverse('recover-password-link')
        response = self.client.post(
            url, data={'email': user.email},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == user.email

    def test_update_password_after_recovery(self):
        """
        Ensure that the password gets updated once we recover it
        """
        user = self.create_user(email='test_user1@gmail.com')
        url = reverse('update-password')
        updatedData = {
            'email': user.email,
            'password': '123update123'
        }
        response = self.client.patch(
            url, data=updatedData,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['password'] != user.password
