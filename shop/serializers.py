"""
Serializers for Shop models
"""
from rest_framework import serializers
from .models import Cart


class CartSerializer(serializers.Serializer):
    """Serializer for Cart model"""
    class Meta:
        model = Cart
        fields = "__all__"
