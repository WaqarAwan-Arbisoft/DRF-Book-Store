"""
URLs for the User APIs
"""


from django.urls import path
from . import views
urlpatterns = [
    path('confirm-email/', views.ConfirmEmailView.as_view(), name='confirm-email'),
    path('register/',
         views.CompleteRegistration.as_view(), name='register'),
    path('login/', views.CreateTokenView.as_view(), name='login'),
    path('update/', views.UpdateUserView.as_view(), name='update'),
    path('fetch-all/', views.ListAllView.as_view(), name='list-all')
]
