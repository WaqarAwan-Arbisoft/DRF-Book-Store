"""
Shop Views
"""
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer
from .models import Cart


class CreateCartView(generics.CreateAPIView):
    """Create cart for the user"""
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """Retrieve and Update view for the """
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Cart.objects.get(owner=self.request.user)
