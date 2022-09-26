"""
Serializers for the Shop Models
"""
from dataclasses import fields
from rest_framework import serializers

from shop.models import Cart, Item, Order, OrderedItem, Review
from books.serializers import BookSerializer, OrderBookSerializer
from user.serializers import UserCommentSerializer


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


class CheckStockSerializer(serializers.ModelSerializer):
    """Serializer to check the stock availability"""
    items = ItemSerializer(many=True)

    class Meta:
        model = Item
        fields = ['items']


class UserReviewSerializer(serializers.ModelSerializer):
    """Serializer for User Review"""

    class Meta:
        model = Review
        fields = ['book', 'comment', 'rating']


class GetReviewSerializer(serializers.ModelSerializer):
    """Serializer to get Book Reviews"""
    user = UserCommentSerializer()

    class Meta:
        model = Review
        fields = "__all__"


class FetchUserReviewSerializer(serializers.ModelSerializer):
    """Serializer to fetch user review"""
    class Meta:
        model = Review
        fields = ['book']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order"""
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemsSerializer(serializers.ModelSerializer):
    """Serializer for the order items"""
    book = OrderBookSerializer()

    class Meta:
        model = OrderedItem
        fields = ['quantity', 'book']
