"""
Serializers for the Shop Models
"""
import stripe

from rest_framework import serializers, exceptions

from books.models import Book
from shop.models import (Cart, Favorite, Item,
                         Like, Order, OrderedItem,
                         Review, StripePayment
                         )
from books.serializers import BookSerializer, OrderBookSerializer
from shop.utils import ShopBusinessLogic
from socialmedia.models import Friendship
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

    def create(self, validated_data):
        """Create a new item in the cart and return"""
        cart, book = ShopBusinessLogic(self.context['request']).is_cart_and_book_available(
            bookId=validated_data['book'].id
        )
        if (book.stock == 0):
            raise exceptions.APIException('Book is out of stock')
        if (book.stock < validated_data['quantity']):
            raise exceptions.APIException(
                'Not enough quantity available at the stock.')
        return ShopBusinessLogic(self.context['request']).add_to_cart(
            book=book, cart=cart,
            quantity=validated_data['quantity']
        )

    def update(self, instance, validated_data):
        try:
            ShopBusinessLogic(self.context['request']).updateQuantity(
                item=instance,
                cart=instance.cart,
                book=instance.book,
                quantity=validated_data['quantity']
            )
        except:
            raise exceptions.APIException('An error occurred.')
        return super().update(instance, validated_data)


class RemoveItemSerializer(serializers.ModelSerializer):
    """Remove item serializer"""
    class Meta:
        model = Item
        fields = ['book']

    def update(self, instance, validated_data):
        try:
            cart = Cart.objects.get(owner=self.context['request'].user)
        except:
            raise exceptions.NotFound(
                detail="Item does not exists.")
        cart.totalPrice = cart.totalPrice-instance.quantity * \
            validated_data['book'].price
        cart.totalQty = cart.totalQty-instance.quantity
        cart.save()
        instance.delete()
        if (len(cart.items.all())) == 0:
            cart.delete()
        return validated_data


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

    def create(self, validated_data):
        """Check the items and stock"""
        for item in validated_data['items']:
            if (item['book'].stock < item['quantity']):
                raise exceptions.APIException(
                    f"Not enough quantity available for {item['book'].name}. You selected {item['quantity']} and {item['book'].stock} is available.")
        return super().create(validated_data)


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


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorite model"""
    class Meta:
        model = Favorite
        fields = []

    def create(self, validated_data):
        favorite = None
        try:
            book = Book.objects.get(
                id=self.context.get('view').kwargs.get('bookId'))
        except:
            raise exceptions.ValidationError(
                {"detail": "No book found with this ID"})
        try:
            favorite = Favorite.objects.create(book=book,
                                               user=self.context['request'].user)
        except:
            raise exceptions.ValidationError(
                {"detail": "Already added to favorites."})

        ShopBusinessLogic(self.context['request']).notify_friends(
            book=book,
            favorite=favorite
        )
        return favorite


class FetchFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for fetching the favorites of a user"""
    book = BookSerializer()

    class Meta:
        model = Favorite
        fields = '__all__'


class LikeBookSerializer(serializers.ModelSerializer):
    """Serializer for liking a book"""
    class Meta:
        model = Like
        fields = []

    def create(self, validated_data):
        like = None
        try:
            book = Book.objects.get(
                id=self.context.get('view').kwargs.get('bookId'))
        except:
            raise exceptions.ValidationError(
                {'detail': 'No book found with this ID'}
            )
        try:
            like = Like.objects.create(
                book=book, user=self.context['request'].user)
        except:
            raise exceptions.ValidationError(
                {'detail': 'Already liked.'}
            )
        ShopBusinessLogic(self.context['request']).notify_friends(
            book=book,
            like=like
        )
        return like


class FetchLikeSerializer(serializers.ModelSerializer):
    """Serializer for fetching the liked book of a user"""
    class Meta:
        model = Like
        fields = '__all__'


class StripePaymentSerializer(serializers.ModelSerializer):
    """Serializer for stripe payment"""
    class Meta:
        model = StripePayment
        fields = '__all__'

    def create(self, validated_data):
        email = validated_data['email']
        amount = validated_data['amount']
        payment_method_id = validated_data['payment_method_id']
        cart = None
        try:
            cart = Cart.objects.get(owner=self.context['request'].user)
        except:
            raise exceptions.APIException(
                detail="No cart exists for this user")
        customer_data = stripe.Customer.list(email=email).data
        if len(customer_data) == 0:
            customer = stripe.Customer.create(
                email=email,
                payment_method=payment_method_id
            )
        else:
            customer = customer_data[0]
        try:
            stripe.PaymentIntent.create(
                customer=customer,
                payment_method=payment_method_id,
                currency='usd',
                amount=amount,
                confirm=True
            )
        except:
            exceptions.APIException(
                detail='Unable to make payment. Please try again later.')

        ShopBusinessLogic(self.context['request']).finalizeOrder(cart)
        return super().create(validated_data)
