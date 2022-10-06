"""
Model for Book
"""
from django.db import models


class Book(models.Model):
    """Book in the system"""
    name = models.CharField(max_length=150, blank=False, unique=True)
    author = models.CharField(max_length=150)
    publishDate = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    noOfPages = models.IntegerField()
    image = models.ImageField(upload_to="book-covers", default="")
    stock = models.IntegerField(default=10)
