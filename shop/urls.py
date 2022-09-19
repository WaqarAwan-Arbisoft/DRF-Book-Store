"""
URLs for Shop
"""

from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/',
         views.AddToCartView.as_view(), name='add-to-card'),
    path('fetch-items/', views.FetchCartItemsView.as_view(),
         name='fetch-cart-items'),
    path('get-update-delete-cart/', views.GetDestroyCartView.as_view(),
         name='get-update-delete-cart'),
    path('cart-item/update-quantity/',
         views.UpdateItemQuantityView.as_view(), name='update-item-quantity'),
    path('cart-item/remove-item/',
         views.RemoveItemView.as_view(), name='remove-item'),
    path('save-stripe-info/', views.save_stripe_info, name='save-payment'),
    path('add-review/', views.AddReviewView.as_view(), name='add-review'),
    path('fetch-reviews/<int:id>',
         views.GetBookReview.as_view(), name='fetch-reviews')
]
