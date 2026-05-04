from django.contrib import admin
from .models import Category, FortuneCookie, UserProfile, UserPrediction, FavoriteCookie

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(FortuneCookie)
class FortuneCookieAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'is_active', 'usage_count', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('text',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'favorite_category')
    list_filter = ('favorite_category',)


@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'cookie', 'received_at', 'is_favorite')
    list_filter = ('is_favorite', 'received_at')


@admin.register(FavoriteCookie)
class FavoriteCookieAdmin(admin.ModelAdmin):
    list_display = ('user', 'cookie', 'added_at')
    list_filter = ('added_at',)