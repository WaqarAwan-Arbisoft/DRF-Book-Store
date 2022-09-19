from django.contrib import admin

# Register your models here.
from .models import Cart, Item, Review

admin.site.register(Cart)
admin.site.register(Item)
admin.site.register(Review)
