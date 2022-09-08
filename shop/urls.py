"""
URL for cart
"""

from django.urls import path
from . import views

urlpatterns = [
    path('create-cart/', views.CreateCartView.as_view(), name='create-cart'),
    path('fetch-cart/', views.RetrieveView.as_view(), name='fetch-cart'),
    path('add-to-cart/',
         views.AddToCartView.as_view(), name='add-to-card'),
    path('remove-cart/', views.RemoveCartView.as_view(), name='remove-cart')
]
