"""
Test the books app features
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from books.models import Book


class BooksAppTest(APITestCase):
    """
    Tests for Books Application
    """

    def create_book(self):
        """
        Create a book in the test database
        """
        return Book.objects.create(name='test-book', author='test-author',
                                   description='test-book-description', price=250.00,
                                   noOfPages=250)

    def test_fetch_all_books(self):
        """
        Ensure that all books are getting fetched
        """
        book = self.create_book()
        url = reverse('fetch-all')
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_get_book(self):
        """
        Ensure that book info is returned
        """
        book = self.create_book()
        url = reverse('fetch-book', kwargs={'pk': book.id})
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == book.name
