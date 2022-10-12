"""
Test the User app features
"""

from django.urls import reverse
from rest_framework.test import APITestCase
from user import views
from rest_framework import status
from django.contrib.auth import get_user_model


class UserAppTests(APITestCase):
    """
    Tests for User Application
    """

    def test_register_and_save_temp_user(self):
        """
        Ensure we can register the user with data 
        and save the user as a temporary user
        """
        data = {
            'name': 'Test User',
            'email': 'test_user@gmail.com',
            'password': '123testing123'
        }
        url = reverse("confirm-email")
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert get_user_model().objects.get().email == data['email']
        assert get_user_model().objects.get().tempUser == True
        assert get_user_model().objects.count() == 1
