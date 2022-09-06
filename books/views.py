"""
Views for the Book APIs
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework import generics

from .models import Book
from .serializers import BookDetailSerializer, BookSerializer


class CreateBookView(generics.CreateAPIView):
    """Create a new Book(Admin only)"""
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class ListBooksView(generics.ListAPIView):
    """List all the books available"""
    serializer_class = BookSerializer
    queryset = Book.objects.all()


class GetBookView(generics.RetrieveAPIView):
    """Get a book with id"""
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()


class UpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Update and Delete a book"""
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
