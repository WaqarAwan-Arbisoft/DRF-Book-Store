"""
Model for Book
"""
from django.db import models
from django.conf import settings


class Book(models.Model):
    """Book in the system"""
    name = models.CharField(max_length=150, blank=False, unique=True, error_messages={
        'required': "Please provide book name"
    })
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='books', on_delete=models.CASCADE)
    publishDate = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    noOfPages = models.IntegerField(blank=True)
    image = models.ImageField(upload_to="book-covers", default="")

    def __str__(self):
        return f"Book name is {self.name} written by {self.author.name}"
