"""
Serializers for the Shop Models
"""
from rest_framework import serializers

from shop.models import Cart, Item
from books.serializers import BookSerializer


class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart model"""
    class Meta:
        model = Cart
        fields = ['owner', 'totalPrice', 'totalQty']


class ItemSerializer(serializers.ModelSerializer):
    """Item serializer"""
    class Meta:
        model = Item
        fields = ['book', 'quantity']


class RemoveItemSerializer(serializers.ModelSerializer):
    """Remove item serializer"""
    class Meta:
        model = Item
        fields = ['book']


class GetCartSerializer(serializers.ModelSerializer):
    """Serializer to Get Cart Data"""
    book = BookSerializer()

    class Meta:
        model = Item
        fields = ['book', 'quantity']
