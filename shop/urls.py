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
    path('fetch-reviews/<int:id>/',
         views.GetBookReview.as_view(), name='fetch-reviews'),
    path('check-stock/', views.CheckStockView.as_view(), name='check-stock'),
    path('purchase-from-stock/', views.PurchaseFromStock.as_view(),
         name='purchase-from-stock'),
    path('fetch-orders/', views.FetchOrdersView.as_view(), name='fetch-orders'),
    path('fetch-order-detail/<int:pk>/', views.FetchOrderDetail.as_view(),
         name='fetch-order-detail'),
    path('add-to-favorite/<int:bookId>/',
         views.AddToFavoriteView.as_view(), name='add-to-favorite'),
    path('fetch-favorites/', views.FetchFavoritesView.as_view(),
         name='fetch-favorites'),
    path('is-favorite/<int:bookId>/',
         views.CheckIsFavoriteView.as_view(), name='is-favorite'),
    path('remove-favorite/<int:bookId>/',
         views.RemoveFavorite.as_view(), name='remove-favorite'),
    path('like-book/<int:bookId>/', views.LikeBookView.as_view(), name='like-book'),
    path('is-liked/<int:bookId>/',
         views.CheckIfLikedView.as_view(), name='is-liked'),
    path('remove-like/<int:bookId>/',
         views.RemoveLikeView.as_view(), name='remove-like')
]
