"""
This module defines the business logics for Social Media App
"""

from rest_framework import exceptions

from socialmedia.models import Friendship


class SocialMediaBusinessLogic():
    """Defines the business login for Social Media App"""

    def return_if_friends(self, user, otherUser, errMsg):
        """Check if friends then return"""
        try:
            return Friendship.objects.get(
                initiatedBy__id=otherUser,
                initiatedTowards=user,
                is_accepted=True
            )
        except:
            try:
                return Friendship.objects.get(
                    initiatedBy=user,
                    initiatedTowards__id=otherUser,
                    is_accepted=True
                )
            except:
                raise exceptions.APIException(errMsg)

    def return_if_request_sent(self, user, otherUser, errMsg):
        """Check if request sent then return"""
        try:
            return Friendship.objects.get(
                initiatedBy__id=otherUser,
                initiatedTowards=user,
                is_accepted=False
            )
        except:
            try:
                return Friendship.objects.get(
                    initiatedBy=user,
                    initiatedTowards__id=otherUser,
                    is_accepted=False
                )
            except:
                raise exceptions.APIException(errMsg)

    def check_if_friendship_exists(self, user, otherUser, errMsg):
        """Check if friends exists and return"""
        try:
            return Friendship.objects.get(
                initiatedBy__id=otherUser,
                initiatedTowards=user
            )
        except:
            try:
                return Friendship.objects.get(
                    initiatedBy=user,
                    initiatedTowards__id=otherUser
                )
            except:
                raise exceptions.APIException(errMsg)
