"""
This module defines the business logics for Shop app
"""

from rest_framework import exceptions
from django.db.models import F, Q

from books.models import Book
from shop.models import Cart, Item, Order, OrderedItem
from socialmedia.models import BookFeed, Friendship


class ShopBusinessLogic(object):
    """Defines the business login for Social Media App"""

    def __init__(self, request):
        self.request = request

    def is_cart_and_book_available(self, bookId):
        """
        Check if cart and book is available, return it else raise exception
        """
        book = None
        cart, created = Cart.objects.get_or_create(owner=self.request.user)
        if not cart:
            raise exceptions.ParseError('An error occurred.')
        try:
            book = Book.objects.get(pk=bookId)
        except:
            raise exceptions.NotFound('No Book found with this ID')

        return (cart, book)

    def add_to_cart(self, book, cart, quantity):
        """
        Add the item to cart
        """
        item, created = Item.objects.get_or_create(book=book, cart=cart,
                                                   defaults={
                                                       'quantity': quantity}
                                                   )
        if not created:
            item.quantity = int(item.quantity) + int(quantity)
        item.save()
        cart.totalQty = int(cart.totalQty) + \
            int(quantity)
        cart.totalPrice = float(cart.totalPrice) + \
            float(float(book.price)*int(quantity))
        cart.save()
        return {'book': item.book, 'quantity': item.quantity}

    def finalizeOrder(self, cart):
        """Initiate the order and add the items"""
        cartItems = None
        order = None

        cartItems = Item.objects.filter(cart=cart)
        order = Order.objects.create(
            owner=self.request.user, totalPrice=cart.totalPrice,
            totalQty=cart.totalQty
        )
        for item in cartItems:
            OrderedItem.objects.create(
                order=order, book=item.book,
                quantity=item.quantity
            )

    def updateQuantity(self, item, cart, book, quantity):
        """Update the item quantity in cart"""
        oldQuantity = None
        newQuantity = int(quantity)
        try:
            oldQuantity = item.quantity
            item.quantity = newQuantity
            item.save()
            cart.totalQty = cart.totalQty-oldQuantity
            cart.totalPrice = cart.totalPrice-book.price*oldQuantity
            cart.totalQty = cart.totalQty+newQuantity
            cart.totalPrice = cart.totalPrice+book.price*newQuantity
            cart.save()
        except:
            raise exceptions.ValidationError('An error occurred.')

    def notify_friends(self, book, review=None, like=None, favorite=None):
        """Notify friends about an event"""
        friends = Friendship.objects.filter((Q(initiatedBy=self.request.user) | Q(
            initiatedTowards=self.request.user)), is_accepted=True).values_list('id', flat=True)
        feed = None
        if review:
            feed = BookFeed.objects.create(
                creator=self.request.user, book=book,
                review=review
            )
        elif like:
            feed = BookFeed.objects.create(
                creator=self.request.user, book=book,
                like=like
            )
        elif favorite:
            feed = BookFeed.objects.create(
                creator=self.request.user, book=book,
                favorite=favorite
            )
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
