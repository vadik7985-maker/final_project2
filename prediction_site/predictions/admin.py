from django.contrib import admin
from .models import Category, FortuneCookie, UserProfile, UserPrediction, FavoriteCookie, Achievement, UserAchievement

@admin.register(Category) #дек для отобр админки
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description') # поля в списке записей
    search_fields = ('name',) # искать по

@admin.register(FortuneCookie)
class FortuneCookieAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'is_active', 'usage_count', 'created_at')
    list_filter = ('category', 'is_active') # бок панель
    search_fields = ('text',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'favorite_category')
    list_filter = ('favorite_category',)


@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin): #какое предс у кого
    list_display = ('user', 'cookie', 'received_at', 'is_favorite')
    list_filter = ('is_favorite', 'received_at')


@admin.register(FavoriteCookie)
class FavoriteCookieAdmin(admin.ModelAdmin):
    list_display = ('user', 'cookie', 'added_at')
    list_filter = ('added_at',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'required_predictions', 'required_favorites', 'required_category_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('required_predictions', 'required_favorites', 'required_category_count', 'is_active')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement', 'earned_at')
    search_fields = ('user__username',)