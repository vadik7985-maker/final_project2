from django.contrib import admin
from .models import Category, FortuneCookie, UserProfile, UserPrediction, FavoriteCookie

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

