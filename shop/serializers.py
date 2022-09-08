"""
Serializers for Shop models
"""
from dataclasses import field
from rest_framework import serializers
from .models import Cart
from books.serializers import BookSerializer
from books.models import Book


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model"""
    class Meta:
        model = Cart
        fields = []


class UpdateCartSerializer(serializers.ModelSerializer):
    """Serializer for updating cart"""
    class Meta:
        model = Cart
        fields = '__all__'
        extra_kwargs = {'owner': {'read_only': True}, 'totalPrice': {
            'read_only': True}, 'totalQty': {'read_only': True}}

    def update(self, instance, validated_data):
        print(instance)
        print(validated_data)
        return super().update(instance, validated_data)


class GetCartSerializer(serializers.ModelSerializer):
    """Serializer for viewing the cart"""
    items = BookSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['owner', 'items', 'totalPrice', 'totalQty']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for cart"""
    quantity = serializers.IntegerField()
    bookId = serializers.IntegerField()
    extra_kwargs = {'quantity': {'required': True, 'allow_blank': False},
                    'bookId': {'required': True, 'allow_blank': False}}

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
