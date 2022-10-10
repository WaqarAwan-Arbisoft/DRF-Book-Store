"""
Models for the social media app
"""

from django.db import models
from django.contrib.auth import get_user_model

from books.models import Book
from shop.models import Favorite, Like, Review


class Friendship(models.Model):
    """Model that contains friendship data"""
    initiatedBy = models.ForeignKey(
        get_user_model(), related_name='frSender', on_delete=models.CASCADE)
    initiatedTowards = models.ForeignKey(
        get_user_model(), related_name='frReceiver', on_delete=models.CASCADE)
    creation = models.DateField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)


class FriendshipNotification(models.Model):
    """Model for notification about friendships"""
    sender = models.ForeignKey(
        get_user_model(), related_name='requestSender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        get_user_model(), related_name='requestReceiver', on_delete=models.CASCADE)
    creation = models.DateField(auto_now_add=True)


class BookFeed(models.Model):
    """Model that contains Notifications data"""
    notify = models.ManyToManyField(
        get_user_model(), related_name='notificationFor')
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True)
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE, null=True)
    like = models.ForeignKey(Like, on_delete=models.CASCADE, null=True)
