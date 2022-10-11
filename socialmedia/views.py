"""
Views for social interactions
"""

from rest_framework import (generics, permissions,
                            authentication, exceptions,
                            pagination
                            )

from socialmedia.utils import SocialMediaBusinessLogic
from socialmedia.serializers import (AcceptRequestSerializer, AddFriendSerializer,
                                     BookFeedSerializer, FetchFriendshipSerializer,
                                     FriendsSerializer, FriendshipNotificationSerializer,
                                     FriendshipSerializer, RejectRequestSerializer
                                     )
from .models import (BookFeed, Friendship,
                     FriendshipNotification
                     )


class AddAsFriendView(generics.CreateAPIView):
    """Create a new friendship"""
    serializer_class = AddFriendSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class FetchFriendRequestsView(generics.ListAPIView):
    """Fetch all the friend request of a user"""
    serializer_class = FriendsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Friendship.objects.filter(
            initiatedTowards=self.request.user,
            is_accepted=False
        )


class AcceptRequestView(generics.UpdateAPIView):
    """Accept the request"""
    serializer_class = AcceptRequestSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_object(self):
        try:
            return Friendship.objects.get(
                initiatedBy=self.request.data['initiatedBy'],
                initiatedTowards=self.request.user
            )
        except:
            raise exceptions.ValidationError('An error occurred.')


class RemoveRequestView(generics.DestroyAPIView):
    """Remove the request initiated by the user"""
    serializer_class = RejectRequestSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return SocialMediaBusinessLogic.return_if_request_sent(
            user=self.request.user,
            otherUser=self.kwargs.get('userId'),
            errMsg="An error occurred.")


class FetchFriendshipNotifications(generics.ListAPIView):
    """Fetch all the friendship notification of a user"""
    serializer_class = FriendshipNotificationSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    PAGE_SIZE = 4
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return FriendshipNotification.objects.filter(sender=self.request.user)


class FetchFeedView(generics.ListAPIView):
    """Fetch the feed of a particular user"""
    serializer_class = BookFeedSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    PAGE_SIZE = 4
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return BookFeed.objects.filter(notify=self.request.user).order_by('-id')


class RemoveFriendView(generics.DestroyAPIView):
    """Remove friend from the friendship"""
    serializer_class = FriendshipSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return SocialMediaBusinessLogic.return_if_friends(
            user=self.request.user,
            otherUser=self.kwargs.get('userId'),
            errMsg="Users are not friends.")


class FetchFriendshipView(generics.RetrieveAPIView):
    serializer_class = FetchFriendshipSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return SocialMediaBusinessLogic().check_if_friendship_exists(
            user=self.request.user,
            otherUser=self.kwargs.get('userId'),
            errMsg="Users are not friends.")
