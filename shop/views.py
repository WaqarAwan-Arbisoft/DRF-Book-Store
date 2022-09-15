"""
Views for the Shop
"""
from rest_framework import generics, exceptions
from rest_framework import authentication
from rest_framework import permissions
from books.models import Book
from shop.models import Cart, Item
from shop.serializers import CartSerializer, GetCartSerializer, ItemSerializer, RemoveItemSerializer


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
        print()
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
