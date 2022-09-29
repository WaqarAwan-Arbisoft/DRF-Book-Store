"""
Views for the Shop
"""
from rest_framework import generics, exceptions
from rest_framework import authentication
from rest_framework import permissions
from books.models import Book
from bookshop.settings import env
from shop.models import Cart, Favorite, Item, Like, Order, OrderedItem, Review
from shop.serializers import CartSerializer, CheckStockSerializer, FavoriteSerializer, FetchFavoriteSerializer, FetchLikeSerializer, FetchUserReviewSerializer, GetCartSerializer, GetReviewSerializer, ItemSerializer, LikeBookSerializer, OrderItemsSerializer, OrderSerializer, RemoveItemSerializer, UserReviewSerializer
import stripe
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from django.db.models import Q
from socialmedia.models import BookFeed, Friendship


class AddToCartView(generics.CreateAPIView):
    """Add Items to cart View"""
    serializer_class = ItemSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cart = None
        book = None
        try:
            cart = Cart.objects.get(owner=self.request.user)
        except:
            cart = Cart.objects.create(owner=self.request.user)
        try:
            book = Book.objects.get(pk=serializer.validated_data['book'].id)
        except:
            raise exceptions.APIException('No Book found with this ID')
        if (book.stock == 0):
            raise exceptions.APIException('Book is out of stock')
        if (book.stock < serializer.validated_data['quantity']):
            raise exceptions.APIException(
                'Not enough quantity available at the stock.')
        try:
            item = Item.objects.get(book=book, cart=cart)
            item.quantity = int(item.quantity) + \
                int(serializer.validated_data['quantity'])
        except:
            item = Item.objects.create(book=book, cart=cart,
                                       quantity=serializer.validated_data['quantity'])
        item.save()
        cart.totalQty = int(cart.totalQty) + \
            int(serializer.validated_data['quantity'])
        cart.totalPrice = float(cart.totalPrice) + \
            float(float(book.price)*int(serializer.validated_data['quantity']))
        cart.save()


class FetchCartItemsView(generics.ListAPIView):
    """Fetch all items of the cart"""
    serializer_class = GetCartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            cart = Cart.objects.get(owner=self.request.user)
        except:
            return []
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
            raise exceptions.ValidationError(
                {"detail": "No cart exists for this user yet."})

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
            raise exceptions.ValidationError(
                {"detail": "An error occurred."})
        return item

    def perform_update(self, serializer):
        cart = None
        book = None
        item = None
        oldQuantity = None
        newQuantity = int(serializer.validated_data['quantity'])
        try:
            cart = Cart.objects.get(owner=self.request.user)
            book = Book.objects.get(pk=serializer.validated_data['book'].id)
            item = Item.objects.get(book=book, cart=cart)
            oldQuantity = item.quantity
            item.quantity = int(newQuantity)
            item.save()
            cart.totalQty = cart.totalQty-oldQuantity
            cart.totalPrice = cart.totalPrice-book.price*oldQuantity
            cart.totalQty = cart.totalQty+newQuantity
            cart.totalPrice = cart.totalPrice+book.price*newQuantity
            cart.save()

        except:
            raise exceptions.APIException('An error occurred.')


class RemoveItemView(generics.CreateAPIView):
    """Remove Item from the cart"""
    serializer_class = RemoveItemSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cart = None
        try:
            cart = Cart.objects.get(owner=self.request.user)
        except:
            raise exceptions.ValidationError(
                {"detail": "No cart exists for this user yet."})
        try:
            item = Item.objects.get(
                cart=cart, book__id=serializer.validated_data['book'].id)
        except:
            raise exceptions.ValidationError(
                {"detail": "No item exists with this id for this user."})

        cart.totalPrice = cart.totalPrice-item.quantity * \
            serializer.validated_data['book'].price
        cart.totalQty = cart.totalQty-item.quantity
        cart.save()
        item.delete()
        if (len(cart.items.all())) == 0:
            cart.delete()


stripe.api_key = env('STRIPE_API_KEY')


def initiateOrder(request):
    cart = None
    cartItems = None
    order = None
    try:
        cart = Cart.objects.get(owner=request.user)
    except:
        raise exceptions.APIException("No cart exists for this user")

    cartItems = Item.objects.filter(cart=cart)
    order = Order.objects.create(
        owner=request.user, totalPrice=cart.totalPrice, totalQty=cart.totalQty)
    for item in cartItems:
        OrderedItem.objects.create(
            order=order, book=item.book, quantity=item.quantity)


@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def save_stripe_info(request):
    data = request.data
    email = data['email']
    amount = data['amount']
    payment_method_id = data['payment_method_id']
    extra_msg = ''

    customer_data = stripe.Customer.list(email=email).data
    if len(customer_data) == 0:
        customer = stripe.Customer.create(
            email=email, payment_method=payment_method_id)
    else:
        customer = customer_data[0]
        extra_msg = "Customer already existed."
    try:
        stripe.PaymentIntent.create(
            customer=customer,
            payment_method=payment_method_id,
            currency='usd',
            amount=amount,
            confirm=True)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={'message': 'Failure', 'data': {
                            'customer_id': customer.id, 'extra_msg': extra_msg}
                        })

    initiateOrder(request)
    return Response(status=status.HTTP_200_OK,
                    data={'message': 'Success', 'data': {
                        'customer_id': customer.id, 'extra_msg': extra_msg}
                    })


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
            raise exceptions.APIException('No Book found with this ID')

        rev = serializer.save(user=self.request.user)
        friends = Friendship.objects.filter((Q(initiatedBy=self.request.user) | Q(
            initiatedTowards=self.request.user)), is_accepted=True).values_list('id', flat=True)
        feed = BookFeed.objects.create(
            creator=self.request.user, book=book, review=rev)
        foundFriend = None
        for friend in friends:
            try:
                foundFriend = Friendship.objects.get(
                    id=friend, initiatedBy=self.request.user)
                feed.notify.add(foundFriend.initiatedTowards)
            except:
                foundFriend = Friendship.objects.get(
                    id=friend, initiatedTowards=self.request.user)
                feed.notify.add(foundFriend.initiatedBy)

        feed.save()


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

    def perform_create(self, serializer):
        """Check the items and stock"""
        for item in serializer.validated_data['items']:
            if (item['book'].stock < item['quantity']):
                raise exceptions.APIException(
                    f"Not enough quantity available for {item['book'].name}. You selected {item['quantity']} and {item['book'].stock} is available.")


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
            order__id=self.kwargs.get('pk'), order__owner=self.request.user)
        if (len(orderedItems) == 0):
            raise exceptions.APIException("No Item exists")
        return orderedItems


class AddToFavoriteView(generics.CreateAPIView):
    """View to add a book to user's favorites"""
    serializer_class = FavoriteSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            book = Book.objects.get(id=self.kwargs['bookId'])
        except:
            raise exceptions.ValidationError(
                {"detail": "No book found with this ID"})

        favorite = Favorite.objects.create(book=book, user=self.request.user)

        friends = Friendship.objects.filter((Q(initiatedBy=self.request.user) | Q(
            initiatedTowards=self.request.user)), is_accepted=True).values_list('id', flat=True)
        feed = BookFeed.objects.create(
            creator=self.request.user, book=book, favorite=favorite)
        foundFriend = None
        for friend in friends:
            try:
                foundFriend = Friendship.objects.get(
                    id=friend, initiatedBy=self.request.user)
                feed.notify.add(foundFriend.initiatedTowards)
            except:
                foundFriend = Friendship.objects.get(
                    id=friend, initiatedTowards=self.request.user)
                feed.notify.add(foundFriend.initiatedBy)

        feed.save()
        return favorite


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
            raise exceptions.APIException("No book found with this ID")
        try:
            return Favorite.objects.get(book=book, user=self.request.user)
        except:
            raise exceptions.APIException("Not marked as favorite")


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
            raise exceptions.APIException("No book found with this ID")
        try:
            return Favorite.objects.get(book=book, user=self.request.user)
        except:
            raise exceptions.APIException("Not marked as favorite")


class LikeBookView(generics.CreateAPIView):
    """Like the book"""
    serializer_class = LikeBookSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            book = Book.objects.get(id=self.kwargs['bookId'])
        except:
            raise exceptions.ValidationError(
                {"detail": "No book found with this ID"})

        like = Like.objects.create(book=book, user=self.request.user)

        friends = Friendship.objects.filter((Q(initiatedBy=self.request.user) | Q(
            initiatedTowards=self.request.user)), is_accepted=True).values_list('id', flat=True)
        feed = BookFeed.objects.create(
            creator=self.request.user, book=book, like=like)
        foundFriend = None
        for friend in friends:
            try:
                foundFriend = Friendship.objects.get(
                    id=friend, initiatedBy=self.request.user)
                feed.notify.add(foundFriend.initiatedTowards)
            except:
                foundFriend = Friendship.objects.get(
                    id=friend, initiatedTowards=self.request.user)
                feed.notify.add(foundFriend.initiatedBy)

        feed.save()
        return like


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
            raise exceptions.APIException("No book found with this ID")
        try:
            return Like.objects.get(book=book, user=self.request.user)
        except:
            raise exceptions.APIException("Not liked.")


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
            raise exceptions.APIException("No book found with this ID")
        try:
            return Like.objects.get(book=book, user=self.request.user)
        except:
            raise exceptions.APIException("Not liked.")
