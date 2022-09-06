"""
Views for the Book APIs
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Book
from .serializers import BookDetailSerializer, BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """View to manage book APIs"""
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Return the serializer class for the request"""
        if self.action == 'list':
            return BookSerializer
        return BookDetailSerializer
