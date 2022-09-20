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
    path('fetch-all/', views.ListAllView.as_view(), name='list-all'),
    path('fetch-user/', views.GetUserData.as_view(), name='fetch-user-data'),
    path('recover-password-link/', views.EmailRecoveryLink.as_view(),
         name='recover-password-link'),
    path('recovery/<str:token>/', views.CheckTokenAvailability.as_view(),
         name='check-token-availability'),
    path('update-password/', views.UpdateRecoveredPasswordView.as_view(),
         name='update-password')
]
