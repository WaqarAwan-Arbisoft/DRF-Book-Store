"""
Models for the Shop app
"""
from books.models import Book
from django.db import models
from django.conf import settings


class Cart(models.Model):
    """Model for the cart"""
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    items = models.ManyToManyField(Book, related_name='books')
    totalPrice = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00)
    totalQty = models.IntegerField(default=0)
