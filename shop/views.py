"""
Shop Views
"""
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import AddToCartSerializer, CartSerializer, GetCartSerializer
from .models import Cart
from rest_framework import exceptions
from books.models import Book


class CreateCartView(generics.CreateAPIView):
    """Create cart for the user"""
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except:
            raise exceptions.APIException('Cart already exists for this user')


class AddToCartView(generics.CreateAPIView):
    """Add to Cart for a User"""
    serializer_class = AddToCartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart = None
        book = None
        try:
            cart = Cart.objects.get(owner=self.request.user)
        except:
            raise exceptions.APIException('Please make a cart first.')
        try:
            book = Book.objects.get(pk=serializer.validated_data['bookId'])
        except:
            raise exceptions.APIException('No Book found with this ID')

        cart.items.add(book)
        cart.totalQty = cart.totalQty+serializer.validated_data['quantity']
        cart.totalPrice = cart.totalPrice + \
            (book.price*serializer.validated_data['quantity'])
        cart.save()

        return super().perform_create(serializer)

    def get_queryset(self):
        try:
            return Cart.objects.get(owner=self.request.user)
        except:
            raise exceptions.APIException('Please make a cart first.')


class RetrieveView(generics.ListAPIView):
    """Retrieve view for the cart"""
    serializer_class = GetCartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart = Cart.objects.filter(owner=self.request.user)
        if len(cart) == 0:
            raise exceptions.APIException("No cart created for this user yet!")
        return cart


class RemoveCartView(generics.DestroyAPIView):
    """Delete the existing cart for the user"""
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart = Cart.objects.filter(owner=self.request.user)
        if len(cart) == 0:
            raise exceptions.APIException("No cart created for this user yet!")
        return cart
