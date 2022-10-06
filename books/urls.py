"""
URLs for the Book APIs
"""
from django.urls import path

from . import views

urlpatterns = [
    path('fetch-all/',
         views.ListBooksView.as_view(),
         name='fetch-all'),
    path('fetch-book/<int:pk>/',
         views.GetBookView.as_view(),
         name='fetch-book'),
    path('fetch-top-books/<int:total>/',
         views.FetchTopBooksView.as_view(),
         name='fetch-top-books')
]
