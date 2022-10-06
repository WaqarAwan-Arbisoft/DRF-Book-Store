"""
Serializers for the Book Model
"""
from rest_framework import serializers

from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer Book"""
    class Meta:
        model = Book
        fields = [
            'id', 'name', 'price',
            'author', 'noOfPages', 'image',
            'stock'
        ]
        read_only_fields = ['id']


class BookDetailSerializer(BookSerializer):
    """Serializer for book detail view"""
    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields+['description']


class OrderBookSerializer(serializers.ModelSerializer):
    """Serializer for order details"""
    class Meta:
        model = Book
        fields = [
            'id', 'name', 'price',
            'author', 'noOfPages', 'image'
        ]
        read_only_fields = ['id']


class FetchTopSerializer(serializers.ModelSerializer):
    """Serializer to fetch the top books"""
    class Meta:
        model = Book
        fields = '__all__'
