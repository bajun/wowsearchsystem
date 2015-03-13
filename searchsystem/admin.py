from django.contrib import admin
from .models import Account, Place, Review, Category

admin.site.register(Account)
admin.site.register(Place)
admin.site.register(Review)
admin.site.register(Category)