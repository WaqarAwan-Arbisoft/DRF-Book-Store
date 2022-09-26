from django.contrib import admin

# Register your models here.
from .models import Cart, Item, Order, OrderedItem, Review

admin.site.register(Cart)
admin.site.register(Item)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderedItem)
