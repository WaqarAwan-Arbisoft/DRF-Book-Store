"""
Views for the Shop
"""

import stripe

from rest_framework import generics, exceptions, authentication, permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from bookshop.settings import env
from django.db.models import F
from django.db.models import Q
from shop.utils import ShopBusinessLogic

from socialmedia.models import BookFeed, Friendship
from books.models import Book
from shop.models import (Cart, Favorite, Item,
                         Like, Order, OrderedItem,
                         Review
                         )
from shop.serializers import (CartSerializer, CheckStockSerializer,
                              FavoriteSerializer, FetchFavoriteSerializer,
                              FetchLikeSerializer, GetCartSerializer,
                              GetReviewSerializer, ItemSerializer,
                              LikeBookSerializer, OrderItemsSerializer,
                              OrderSerializer, RemoveItemSerializer, StripePaymentSerializer,
                              UserReviewSerializer
                              )
stripe.api_key = env('STRIPE_API_KEY')


class AddToCartView(generics.CreateAPIView):
    """Add Items to cart View"""
    serializer_class = ItemSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class FetchCartItemsView(generics.ListAPIView):
    """Fetch all items of the cart"""
    serializer_class = GetCartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            cart = Cart.objects.get(owner=self.request.user)
        except:
            raise exceptions.NotFound(
                detail="No Items exists in the cart")
        items = Item.objects.filter(cart=cart)
        return items


class GetDestroyCartView(generics.RetrieveDestroyAPIView):
    """Fetch cart details"""
    serializer_class = CartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart = None
        try:
            cart = Cart.objects.get(owner=self.request.user)
        except:
            raise exceptions.NotFound(
                detail="No cart exists for this user yet.")
        return cart


class UpdateItemQuantityView(generics.UpdateAPIView):
    """Update the Item quantity for a Cart"""
    serializer_class = ItemSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_object(self):
        item = None
        cart = None
        try:
            cart = Cart.objects.get(owner=self.request.user)
            item = Item.objects.get(cart=cart, book=self.request.data['book'])
        except:
            raise exceptions.NotFound(
                detail="An error occurred.")
        return item


class RemoveItemView(generics.UpdateAPIView):
    """Remove Item from the cart"""
    serializer_class = RemoveItemSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_object(self):
        cart = None
        item = None
        try:
            cart = Cart.objects.get(owner=self.request.user)
            item = Item.objects.get(
                cart=cart, book__id=self.request.data['book'])
        except:
            raise exceptions.NotFound(
                detail="Item does not exists.")
        return item


class MakePaymentView(generics.CreateAPIView):
    """Make string payment"""
    serializer_class = StripePaymentSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class AddReviewView(generics.CreateAPIView):
    """API for adding review to the book"""
    serializer_class = UserReviewSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        book = None
        try:
            book = Book.objects.get(pk=serializer.validated_data['book'].id)
        except:
            raise exceptions.NotFound('No Book found with this ID')

        rev = serializer.save(user=self.request.user)
        friends = Friendship.objects.filter((Q(initiatedBy=self.request.user) | Q(
            initiatedTowards=self.request.user)), is_accepted=True).values_list('id', flat=True)


class GetBookReview(generics.ListAPIView):
    """Get all the Reviews of a book"""

    serializer_class = GetReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(book=self.kwargs.get('id')).order_by('-id')


class CheckStockView(generics.CreateAPIView):
    """Check the stock availability with Cart Items"""
    serializer_class = CheckStockSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class PurchaseFromStock(generics.CreateAPIView):
    """Update the stock after purchase"""
    serializer_class = CheckStockSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Perform the update on each book"""
        for item in serializer.validated_data['items']:
            item['book'].stock = F('stock')-item['quantity']
            item['book'].save()


class FetchOrdersView(generics.ListAPIView):
    """Fetch the Orders of a particular user"""
    serializer_class = OrderSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)


class FetchOrderDetail(generics.ListAPIView):
    """Fetch the details of an order"""
    serializer_class = OrderItemsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        orderedItems = OrderedItem.objects.filter(
            order__id=self.kwargs.get('pk'),
            order__owner=self.request.user
        )
        if (len(orderedItems) == 0):
            raise exceptions.ValidationError('No Item exists')
        return orderedItems


class AddToFavoriteView(generics.CreateAPIView):
    """View to add a book to user's favorites"""
    serializer_class = FavoriteSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class FetchFavoritesView(generics.ListAPIView):
    """Fetch all the favorites of a user"""
    serializer_class = FetchFavoriteSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class CheckIsFavoriteView(generics.RetrieveAPIView):
    """Get if a user has marked the book as favorite"""
    serializer_class = FetchFavoriteSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        book = None
        try:
            book = Book.objects.get(id=self.kwargs.get('bookId'))
        except:
            raise exceptions.NotFound("No book found with this ID")
        try:
            return Favorite.objects.get(book=book, user=self.request.user)
        except:
            raise exceptions.NotFound("Not marked as favorite")


class RemoveFavorite(generics.DestroyAPIView):
    """Remove a book from favorites"""
    serializer_class = FetchFavoriteSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        book = None
        try:
            book = Book.objects.get(id=self.kwargs.get('bookId'))
        except:
            raise exceptions.NotFound("No book found with this ID")
        try:
            return Favorite.objects.get(book=book, user=self.request.user)
        except:
            raise exceptions.NotFound("Not marked as favorite")


class LikeBookView(generics.CreateAPIView):
    """Like the book"""
    serializer_class = LikeBookSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class CheckIfLikedView(generics.RetrieveAPIView):
    """Check if a book is liked"""
    serializer_class = FetchLikeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        book = None
        try:
            book = Book.objects.get(id=self.kwargs.get('bookId'))
        except:
            raise exceptions.NotFound('No book found with this ID')
        try:
            return Like.objects.get(book=book, user=self.request.user)
        except:
            raise exceptions.ValidationError('Not liked.')


class RemoveLikeView(generics.DestroyAPIView):
    """Remove the like from a book"""
    serializer_class = FetchLikeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        book = None
        try:
            book = Book.objects.get(id=self.kwargs.get('bookId'))
        except:
            raise exceptions.NotFound('No book found with this ID')
        try:
            return Like.objects.get(book=book, user=self.request.user)
        except:
            raise exceptions.ValidationError('Not liked.')
