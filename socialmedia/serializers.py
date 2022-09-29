"""
Serializers for the social interactions of the users
"""

from rest_framework import serializers, exceptions
from books.serializers import BookSerializer
from shop.serializers import UserReviewSerializer

from user.serializers import UserSerializerPublic
from .models import BookFeed, Friendship, FriendshipNotification
from django.db.models import Q
from django.contrib.auth import get_user_model


class AddFriendSerializer(serializers.ModelSerializer):
    """Serializer for adding a friend"""
    class Meta:
        model = Friendship
        fields = ['initiatedTowards']

    def create(self, validated_data):
        """Create and return a new friend object"""
        try:
            Friendship.objects.get(
                initiatedBy=self.context['request'].user, initiatedTowards=validated_data.get('initiatedTowards'))
        except:
            try:
                Friendship.objects.get(
                    initiatedBy=validated_data.get('initiatedTowards'), initiatedTowards=self.context['request'].user)
            except:
                return Friendship.objects.create(
                    initiatedBy=self.context['request'].user, initiatedTowards=validated_data.get('initiatedTowards'))
        raise exceptions.APIException("Request already sent")


class FriendsSerializer(serializers.ModelSerializer):
    """Serializer for Friend model"""
    initiatedBy = UserSerializerPublic()

    class Meta:
        model = Friendship
        fields = '__all__'


class AcceptRequestSerializer(serializers.ModelSerializer):
    """Serializer to accept the request from a user"""
    class Meta:
        model = Friendship
        fields = ['initiatedBy']

    def update(self, instance, validated_data):
        instance.is_accepted = True
        instance.save()
        FriendshipNotification.objects.create(
            sender=instance.initiatedBy, receiver=self.context['request'].user)
        return instance


class RejectRequestSerializer(serializers.ModelSerializer):
    """Serializer to reject the request from a user"""
    class Meta:
        model = Friendship
        fields = ['initiatedBy']


class FriendshipNotificationSerializer(serializers.ModelSerializer):
    """Serializer for friendship notifications"""
    receiver = UserSerializerPublic()

    class Meta:
        model = FriendshipNotification
        fields = '__all__'


class BookFeedSerializer(serializers.ModelSerializer):
    """Serializer for Book Feed"""
    creator = UserSerializerPublic()
    book = BookSerializer()
    review = UserReviewSerializer()

    class Meta:
        model = BookFeed
        fields = '__all__'
