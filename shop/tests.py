"""
Module for testing the Shop app features
"""

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.urls import reverse

from books.models import Book
from shop.models import Cart, Favorite, Item, Like, Review


class ShopAppTests(APITestCase):
    """
    Test the shop app features
    """

    def create_user_and_set_token_credentials(self, email):
        """
        Create a new permanent user
        """
        data = {
            'email': email,
            'password': '123test123',
            'name': 'test user 2'
        }
        user = get_user_model().objects.create_user(
            email=data['email'], password=data['password'],
            name=data['name'], tempUser=False,
            user_code=123456
        )
        token = Token.objects.create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {0}'.format(token.key)
        )
        return user

    def create_user(self, email):
        """
        Create a user in the database
        """
        data = {
            'email': email,
            'password': '123test123',
            'name': 'test user 2'
        }
        user = get_user_model().objects.create_user(
            email=data['email'], password=data['password'],
            name=data['name'], tempUser=False,
            user_code=123456
        )
        return user

    def create_book(self, name):
        """
        Create a book in the test database
        """
        return Book.objects.create(name=name, author='test-author',
                                   description='test-book-description', price=250.00,
                                   noOfPages=250)

    def create_review(self, book, user):
        """
        Create a review
        """
        return Review.objects.create(
            book=book, comment='Book Review',
            rating=5, user=user
        )

    def add_to_cart(self, user, book):
        """
        Add item to cart
        """
        cart, created = Cart.objects.get_or_create(owner=user)
        Item.objects.get_or_create(book=book, cart=cart,
                                   defaults={
                                       'quantity': 1}
                                   )
        return cart

    def add_to_favorite(self, book, user):
        """
        Add book to user's favorite
        """
        favorite, created = Favorite.objects.get_or_create(book=book,
                                                           user=user)
        return favorite

    def add_to_like(self, book, user):
        """
        Add the book to like.
        """
        like, created = Like.objects.get_or_create(book=book,
                                                   user=user)
        return like

    def fetch_item_from_cart(self, book, cart):
        """
        Fetch item from the cart
        """
        return Item.objects.get(cart=cart, book=book)

    def test_add_to_cart(self):
        """
        Ensure that the user will be able to add items to the
        cart
        """
        book = self.create_book(name="test-book")
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com')
        url = reverse('add-to-card')
        bookData = {
            'book': book.id,
            'quantity': 2
        }
        response = self.client.post(url, data=bookData,
                                    format='json'
                                    )
        assert response.status_code == status.HTTP_201_CREATED
        assert Cart.objects.get(owner=user).items.all()[0].id == book.id
        # Clear up the credentials
        self.client.credentials()
        response = self.client.post(url, data=bookData,
                                    format='json'
                                    )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fetch_cart_items(self):
        """
        Ensure that the user will be able to fetch cart items.
        """
        url = reverse('fetch-cart-items')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        book = self.create_book(name='test-book')
        self.add_to_cart(user=user, book=book)
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        # Clear up the credentials
        self.client.credentials()
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fetch_user_cart(self):
        """
        Ensure that the user will be able to fetch his/her 
        cart
        """
        url = reverse('get-delete-cart')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # Cart will be created when user adds a book
        book = self.create_book(name='test-book')
        self.add_to_cart(user=user, book=book)
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['owner'] == user.id
        # Clear up the credentials
        self.client.credentials()
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_cart_item_quantity(self):
        """
        Ensure that the user's cart gets deleted once its empty.
        """
        url = reverse('update-item-quantity')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        book = self.create_book(name='test-book')
        cart = self.add_to_cart(user=user, book=book)
        item = self.fetch_item_from_cart(cart=cart, book=book)
        assert item.quantity == 1
        # Increase quantity
        data = {
            'book': book.id,
            'quantity': 2
        }
        response = self.client.patch(url, data=data,
                                     format='json'
                                     )
        item = self.fetch_item_from_cart(cart=cart, book=book)
        assert response.status_code == status.HTTP_200_OK
        assert item.quantity == 2
        # Decrease quantity
        data = {
            'book': book.id,
            'quantity': 1
        }
        response = self.client.patch(url, data=data,
                                     format='json'
                                     )
        item = self.fetch_item_from_cart(cart=cart, book=book)
        assert response.status_code == status.HTTP_200_OK
        assert item.quantity == 1

    def test_remove_item_from_user_cart(self):
        """
        Ensure that the user will be able to remove item from
        the cart
        """
        url = reverse('remove-item')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        book = self.create_book(name='test-book')
        self.add_to_cart(user=user, book=book)
        response = self.client.patch(url,
                                     data={
                                         'book': book.id
                                     }, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_add_review(self):
        """
        Ensure that the user will be able to add review
        """
        url = reverse('add-review')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        book = self.create_book(
            name='test-book'
        )
        data = {
            'book': book.id,
            'comment': 'testing comment',
            'rating': 2
        }
        response = self.client.post(
            url, data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        # Clear the credentials
        self.client.credentials()
        response = self.client.post(
            url, data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fetch_book_review(self):
        """
        Ensure that reviews available on a book can be fetched
        """
        book = self.create_book(name='test-book')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        url = reverse('fetch-reviews', kwargs={'bookId': book.id})
        review = self.create_review(
            book=book,
            user=user
        )
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert Review.objects.get().id == review.id

    def test_add_to_favorite(self):
        """
        Ensure that the user will be able to add book to his/her
        favorites list.
        """
        book = self.create_book(name='test-book')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        url = reverse('add-to-favorite', kwargs={'bookId': book.id})
        response = self.client.post(url, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        favorite = Favorite.objects.get()
        assert favorite.book.id == book.id
        assert favorite.user.id == user.id
        """
        Clearing the credentials
        """
        self.client.credentials()
        url = reverse('add-to-favorite', kwargs={'bookId': book.id})
        response = self.client.post(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fetch_favorites(self):
        """
        Ensure that the user will be able to fetch his/her
        favorite books list.
        """
        book = self.create_book(name='test-book')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        favorite = self.add_to_favorite(book=book, user=user)
        url = reverse('fetch-favorites')
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == favorite.id
        """
        Clearing the credentials
        """
        self.client.credentials()
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_is_book_favorite(self):
        """
        Ensure that user will be able to check if the book is
        added to favorite.
        """
        book = self.create_book(name='test-book')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        url = reverse('is-favorite', kwargs={'bookId': book.id})
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        favorite = self.add_to_favorite(book=book, user=user)
        url = reverse('is-favorite', kwargs={'bookId': book.id})
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == favorite.id

    def test_remove_from_favorite(self):
        """
        Ensure that user will be able to remove a book from
        favorites.
        """
        book = self.create_book(name='test-book')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        url = reverse('remove-favorite', kwargs={'bookId': book.id})
        response = self.client.delete(url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        self.add_to_favorite(book=book, user=user)
        url = reverse('remove-favorite', kwargs={'bookId': book.id})
        response = self.client.delete(url, format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_like_book(self):
        """
        Ensure that a user will be able to give like to a 
        book.
        """
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        url = reverse('like-book', kwargs={'bookId': 1})
        response = self.client.post(url, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        book = self.create_book(name='test-book')
        url = reverse('like-book', kwargs={'bookId': book.id})
        response = self.client.post(url, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        like = Like.objects.get()
        assert like.book.id == book.id
        assert like.user.id == user.id
        """
        Clearing the credentials
        """
        self.client.credentials()
        response = self.client.post(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_is_book_liked(self):
        """
        Ensure if the user has liked the book.
        """
        book = self.create_book(name='test-book')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        url = reverse('is-liked', kwargs={'bookId': book.id})
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        like = self.add_to_like(book=book, user=user)
        url = reverse('is-liked', kwargs={'bookId': book.id})
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == like.id

    def test_remove_like(self):
        """
        Ensure that user will be able to remove book from 
        likes list.
        """
        book = self.create_book(name='test-book')
        user = self.create_user_and_set_token_credentials(
            email='test-user@gmail.com'
        )
        url = reverse('remove-like', kwargs={'bookId': book.id})
        response = self.client.delete(url, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.add_to_like(book=book, user=user)
        url = reverse('remove-like', kwargs={'bookId': book.id})
        response = self.client.delete(url, format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT
