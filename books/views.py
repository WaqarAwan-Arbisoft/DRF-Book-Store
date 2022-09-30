"""
Views for the Book APIs
"""
from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework import generics
from rest_framework import pagination
from django.db.models import Count

from shop.models import Like

from .models import Book
from .serializers import BookDetailSerializer, BookSerializer, FetchTopSerializer
from rest_framework.filters import SearchFilter


class CreateBookView(generics.CreateAPIView):
    """Create a new Book(Admin only)"""
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class ListBooksView(generics.ListAPIView):
    """List all the books available"""
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['name']
    PAGE_SIZE = 2
    pagination_class = pagination.LimitOffsetPagination


class GetBookView(generics.RetrieveAPIView):
    """Get a book with id"""
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()


class UpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Update and Delete a book(Admin only)"""
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class FetchTopBooksView(generics.ListAPIView):
    """Fetch most liked books"""
    serializer_class = FetchTopSerializer

    def get_queryset(self):
        booksRequired = self.kwargs.get('total')
        mostLiked = Like.objects.values("book").annotate(
            Count("book")).order_by("-book__count")
        data = []
        for liked in mostLiked:
            data.append(Book.objects.get(id=liked['book']))
        if (mostLiked.count() >= booksRequired):
            return data
        else:
            return data
