"""
URL for cart
"""

from django.urls import path
from . import views

urlpatterns = [
    path('create-cart/', views.CreateCartView.as_view(), name='create-cart'),
    path('cart/', views.RetrieveUpdateView.as_view(),
         name='fetch-update-cart'),
]
