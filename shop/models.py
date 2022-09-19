"""
Models for the Shop app
"""
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from books.models import Book
from django.core.validators import MinValueValidator, MaxValueValidator


class Cart(models.Model):
    """Model for the cart"""
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    items = models.ManyToManyField(
        Book, related_name='items', through='Item')
    totalPrice = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00)
    totalQty = models.IntegerField(default=0)


class Item(models.Model):
    """Item of a cart"""
    quantity = models.IntegerField(
        blank=False, validators=[MinValueValidator(1)])
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['cart', 'book']]


class Review(models.Model):
    """Review of the Book"""
    book = models.ForeignKey(Book, related_name='book',
                             on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    creation = models.DateField(auto_now_add=True, blank=True)
