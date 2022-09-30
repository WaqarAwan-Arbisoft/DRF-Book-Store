"""
Views for social interactions
"""

from rest_framework import generics, permissions, authentication, exceptions
from socialmedia.serializers import AcceptRequestSerializer, AddFriendSerializer, BookFeedSerializer, FriendsSerializer, FriendshipNotificationSerializer, FriendshipSerializer, RejectRequestSerializer
from .models import BookFeed, Friendship, FriendshipNotification
from django.contrib.auth import get_user_model

# Create your views here.


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
        return Friendship.objects.filter(initiatedTowards=self.request.user, is_accepted=False)


class AcceptRequestView(generics.UpdateAPIView):
    """Accept the request"""
    serializer_class = AcceptRequestSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_object(self):
        try:
            return Friendship.objects.get(initiatedBy=self.request.data['initiatedBy'], initiatedTowards=self.request.user)
        except:
            raise exceptions.APIException("An error occurred.")


class RemoveRequestView(generics.DestroyAPIView):
    """Remove the request initiated by the user"""
    serializer_class = RejectRequestSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return Friendship.objects.get(initiatedBy=self.kwargs.get('userId'), initiatedTowards=self.request.user, is_accepted=True)
        except:
            try:
                return Friendship.objects.get(initiatedBy=self.request.user, initiatedTowards=self.kwargs.get('userId'), is_accepted=True)
            except:
                raise exceptions.APIException("Users are not friends.")


class FetchFriendshipNotifications(generics.ListAPIView):
    """Fetch all the friendship notification of a user"""
    serializer_class = FriendshipNotificationSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendshipNotification.objects.filter(sender=self.request.user)


class FetchFeedView(generics.ListAPIView):
    """Fetch the feed of a particular user"""
    serializer_class = BookFeedSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookFeed.objects.filter(notify=self.request.user)


class CheckIsFriendView(generics.RetrieveAPIView):
    """Check if a user is friend"""
    serializer_class = FriendsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return Friendship.objects.get(initiatedBy=self.kwargs.get('userId'), initiatedTowards=self.request.user, is_accepted=True)
        except:
            try:
                return Friendship.objects.get(initiatedBy=self.request.user, initiatedTowards=self.kwargs.get('userId'), is_accepted=True)
            except:
                raise exceptions.APIException("Users are not friends.")


class CheckIsRequestSentView(generics.RetrieveAPIView):
    """Check if the request is sent"""
    serializer_class = FriendsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return Friendship.objects.get(initiatedBy=self.kwargs.get('userId'), initiatedTowards=self.request.user, is_accepted=False)
        except:
            try:
                return Friendship.objects.get(initiatedBy=self.request.user, initiatedTowards=self.kwargs.get('userId'), is_accepted=False)
            except:
                raise exceptions.APIException("Request not sent.")


class RemoveFriendView(generics.DestroyAPIView):
    """Remove friend from the friendship"""
    serializer_class = FriendshipSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):

        try:
            return Friendship.objects.get(initiatedBy=self.kwargs.get('userId'), initiatedTowards=self.request.user, is_accepted=True)
        except:
            try:
                return Friendship.objects.get(initiatedBy=self.request.user, initiatedTowards=self.kwargs.get('userId'), is_accepted=True)
            except:
                raise exceptions.APIException("Users are not friends.")


class IsUserInitiatorView(generics.RetrieveAPIView):
    """Is User the initiator of friendship"""
    serializer_class = FriendshipSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return Friendship.objects.get(initiatedBy=self.request.user, initiatedTowards=self.kwargs.get('userId'))
        except:
            raise exceptions.APIException("Users is not an initiator.")
