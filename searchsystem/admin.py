from django.contrib import admin
from .models import Account, Place, Review, Category, CategoryPlace

admin.site.register(Account)
admin.site.register(Review)
admin.site.register(Category)

class PlaceProfileInline(admin.StackedInline):
    model = CategoryPlace
    extra = 1


class CustomPlaceAdmin(admin.ModelAdmin):
    inlines = [PlaceProfileInline]


admin.site.register(Place, CustomPlaceAdmin)