"""
Test the User app features
"""

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


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

    def create_user_and_set_token_credentials(self, data):
        """
        Create a new permanent user
        """
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

    def create_user(self, data):
        """
        Create a user in the database
        """
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
        data = {
            'name': 'Test User',
            'email': 'test_user1@gmail.com',
            'password': '123testing123'
        }
        self.create_user_and_set_token_credentials(data=data)
        assert get_user_model().objects.get().name == data['name']
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
        data = {
            'name': 'Test User',
            'email': 'test_user1@gmail.com',
            'password': '123testing123'
        }
        self.create_user_and_set_token_credentials(data=data)
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
        data = {
            'name': 'Test User',
            'email': 'test_user1@gmail.com',
            'password': '123testing123'
        }
        self.create_user_and_set_token_credentials(data=data)
        url = reverse('fetch-user-data')
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        """
        Clearing up credentials
        """
        self.client.credentials()
        response = self.client.patch(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fetch_other_profile_data(self):
        """
        Ensure that the user will be able to fetch other
        profiles data but only the public information
        """
        data1 = {
            'name': 'Test User',
            'email': 'test_user1@gmail.com',
            'password': '123testing123'
        }
        data2 = {
            'name': 'Test User',
            'email': 'test_user2@gmail.com',
            'password': '123testing123'
        }
        user1 = self.create_user_and_set_token_credentials(data=data1)
        user2 = self.create_user(data=data2)
        url = reverse('fetch-user-data-public', kwargs={'pk': user2.pk})
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert user1.email != user2.email
        """
        Clearing up credentials
        """
        self.client.credentials()
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert user1.email != user2.email

    def test_password_recovery_email(self):
        """
        Ensure that the app sends the password recovery mail
        """
        data = {
            'name': 'Test User',
            'email': 'test_user1@gmail.com',
            'password': '123testing123'
        }
        self.create_user(data=data)
        url = reverse('recover-password-link')
        response = self.client.post(
            url, data={'email': data['email']},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == data['email']

    def test_update_password_after_recovery(self):
        """
        Ensure that the password gets updated once we recover it
        """
        data = {
            'name': 'Test User',
            'email': 'test_user1@gmail.com',
            'password': '123testing123'
        }
        user = self.create_user(data=data)
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
