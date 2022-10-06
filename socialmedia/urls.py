"""
Module for social interactions
"""

from django.urls import path

from . import views


urlpatterns = [
    path('add-as-friend/',
         views.AddAsFriendView.as_view(),
         name='add-as-friend'
         ),
    path('fetch-friend-requests/',
         views.FetchFriendRequestsView.as_view(),
         name='fetch-friend-requests'
         ),
    path('accept-request/',
         views.AcceptRequestView.as_view(),
         name='accept-request'
         ),
    path('remove-request/<int:userId>/',
         views.RemoveRequestView.as_view(),
         name='remove-request'
         ),
    path('friendship-notifications/',
         views.FetchFriendshipNotifications.as_view(),
         name='friendship-notifications'
         ),
    path('fetch-feed/',
         views.FetchFeedView.as_view(),
         name='fetch-feed'
         ),
    path('remove-friend/<int:userId>/',
         views.RemoveFriendView.as_view(),
         name='remove-friend'
         ),
    path('fetch-friendship/<int:userId>/',
         views.FetchFriendshipView.as_view(),
         name='fetch-friendship')
]
