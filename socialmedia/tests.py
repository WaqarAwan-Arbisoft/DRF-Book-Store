"""
Test the books app features
"""
from datetime import timedelta
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from oauth2_provider.models import Application, AccessToken

from socialmedia.models import Friendship


class SocialMediaAppTest(APITestCase):
    """
    Tests for Social Media App
    """

    def __create_authorization_header(self, token):
        return "Bearer {0}".format(token)

    def __create_token(self, user):

        app, appCreated = Application.objects.get_or_create(
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='https://www.none.com/oauth2/callback',
            name='dummy',
            user=user
        )
        access_token, tokenCreated = AccessToken.objects.get_or_create(
            user=user,
            scope='read write',
            expires=timezone.now() + timedelta(seconds=300),
            token=f'secret-access-token-key-{user.id}',
            application=app
        )
        return access_token

    def create_user_and_set_token_credentials(self, email):
        """
        Create a new permanent user
        """
        data = {
            'email': email,
            'password': '123test123',
            'name': 'test user 2'
        }
        user = get_user_model().objects.create_user(
            email=data['email'], password=data['password'],
            name=data['name'], tempUser=False,
            user_code=123456
        )
        token = self.__create_authorization_header(
            token=self.__create_token(user=user)
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=token
        )
        return user

    def create_user(self, email):
        """
        Create a user in the database
        """
        data = {
            'email': email,
            'password': '123test123',
            'name': 'test user 2'
        }
        user = get_user_model().objects.create_user(
            email=data['email'], password=data['password'],
            name=data['name'], tempUser=False,
            user_code=123456
        )
        return user

    def get_token(self, user):
        """
        Get Auth token for user
        """
        token = self.__create_authorization_header(
            token=self.__create_token(user=user)
        )
        return token

    def create_one_side_friendship(self, user, other):
        """
        Create one side friendship initiated by user towards
        other.
        """
        return Friendship.objects.create(
            initiatedBy=user,
            initiatedTowards=other
        )

    def create_friendship(self, user, other):
        """
        Create friendship between user and other
        """
        return Friendship.objects.create(
            initiatedBy=user,
            initiatedTowards=other,
            is_accepted=True
        )

    def test_add_user_as_friend(self):
        """
        Ensure that the user will be able to add other user
        as friend.
        """
        user = self.create_user_and_set_token_credentials(
            email='book-test-user1@gmail.com'
        )
        otherUser = self.create_user(email='book-test-user2@gmail.com')
        url = reverse('add-as-friend')
        response = self.client.post(url,
                                    data={'initiatedTowards': otherUser.id},
                                    format='json'
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        friendship = Friendship.objects.get()
        self.assertEqual(friendship.initiatedBy, user)
        self.assertEqual(friendship.initiatedTowards, otherUser)
        self.assertEqual(friendship.is_accepted, False)

    def test_fetch_all_friend_requests_of_user(self):
        """
        Ensure that the user can fetch his/her pending friend
        requests.
        """
        url = reverse('fetch-friend-requests')
        # No user signed in
        response = self.client.get(
            url, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        user = self.create_user_and_set_token_credentials(
            email='book-test-user1@gmail.com'
        )
        response = self.client.get(
            url, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        otherUser = self.create_user_and_set_token_credentials(
            email='book-test-user2@gmail.com'
        )
        self.create_one_side_friendship(user=otherUser, other=user)
        token = AccessToken.objects.get(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        response = self.client.get(
            url, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_accept_friend_request(self):
        """
        Ensure user will be able to accept the friend request
        """
        url = reverse('accept-request')
        user1Mail = 'test-user1@gmail.com'
        user2Mail = 'test-user2@gmail.com'
        user1 = self.create_user_and_set_token_credentials(email=user1Mail)
        user2 = self.create_user(email=user2Mail)
        friendship = self.create_one_side_friendship(user=user1, other=user2)
        # checking if the friendship is initiated
        self.assertEqual(Friendship.objects.get(), friendship)
        token = self.get_token(user=user2)
        self.client.credentials(
            HTTP_AUTHORIZATION=token
        )
        response = self.client.patch(
            url, data={'initiatedBy': user1.id}, format='json')
        friendship = Friendship.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(friendship.initiatedBy, user1)
        self.assertEqual(friendship.initiatedTowards, user2)
        self.assertEqual(friendship.is_accepted, True)

    def test_remove_friend_request(self):
        """
        Ensure that user will be able to remove/decline
        friend request from a user.
        """
        user1Mail = 'test-user1@gmail.com'
        user2Mail = 'test-user2@gmail.com'
        user1 = self.create_user_and_set_token_credentials(email=user1Mail)
        user2 = self.create_user(email=user2Mail)
        friendship = self.create_one_side_friendship(user=user1, other=user2)
        # checking if the friendship is initiated
        self.assertEqual(Friendship.objects.get(), friendship)
        url = reverse('remove-request',
                      kwargs={'userId': user1.id}
                      )
        token = self.get_token(user=user2)
        self.client.credentials(
            HTTP_AUTHORIZATION=token
        )
        response = self.client.delete(
            url, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_remove_friend(self):
        """
        Ensure that a user will be able to remove friend
        """
        user1Mail = 'test-user1@gmail.com'
        user2Mail = 'test-user2@gmail.com'
        user1 = self.create_user_and_set_token_credentials(email=user1Mail)
        user2 = self.create_user(email=user2Mail)
        self.create_friendship(user=user1, other=user2)
        friendship = Friendship.objects.get()
        self.assertEqual(friendship.initiatedBy, user1)
        self.assertEqual(friendship.initiatedTowards, user2)
        self.assertEqual(friendship.is_accepted, True)
        url = reverse('remove-friend', kwargs={'userId': user2.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_fetch_friendship(self):
        """
        Ensure that user will be able to fetch friendship
        """
        user1Mail = 'test-user1@gmail.com'
        user2Mail = 'test-user2@gmail.com'
        user1 = self.create_user_and_set_token_credentials(email=user1Mail)
        user2 = self.create_user(email=user2Mail)
        url = reverse('fetch-friendship', kwargs={'userId': user2.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.create_friendship(user=user1, other=user2)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
