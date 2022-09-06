"""
URLs for the Book APIs
"""

from rest_framework.routers import DefaultRouter
from django.urls import include, path

from . import views

router = DefaultRouter()
router.register('', views.BookViewSet)

app_name = 'books'

urlpatterns = [
    path('', include(router.urls)),
]
