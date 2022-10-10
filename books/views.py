"""
Views for the Book APIs
"""
from enum import unique
from rest_framework import generics, pagination
from django.db.models import Count
from rest_framework.filters import SearchFilter

from shop.models import Like
from .models import Book
from .serializers import BookDetailSerializer, FetchTopSerializer


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


class FetchTopBooksView(generics.ListAPIView):
    """Fetch most liked books"""
    serializer_class = FetchTopSerializer

    def get_queryset(self):
        #! Change the query
        booksRequired = self.kwargs.get('total')
        mostLiked = Like.objects.values().annotate(
            Count("book")).order_by("-book__count")[:3]
        data = []
        if mostLiked.count() == booksRequired:
            for liked in mostLiked:
                data.append(Book.objects.get(id=liked['book_id']))
        else:
            for liked in mostLiked:
                data.append(Book.objects.get(id=liked['book_id']))
        return data
