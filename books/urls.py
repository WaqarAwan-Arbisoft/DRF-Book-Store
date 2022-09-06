"""
URLs for the Book APIs
"""
from django.urls import include, path

from . import views

urlpatterns = [
    path('create/', views.CreateBookView.as_view(), name='create-book'),
    path('fetch-all/', views.ListBooksView.as_view(), name='fetch-all'),
    path('fetch-book/<int:pk>', views.GetBookView.as_view(), name='fetch-book'),
    path('updateDestroy/<int:pk>', views.UpdateDestroyView.as_view(),
         name='update-delete-book')
]
