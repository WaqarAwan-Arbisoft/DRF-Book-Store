from django.contrib import admin

# Register your models here.
from .models import Cart, Item

admin.site.register(Cart)
admin.site.register(Item)
