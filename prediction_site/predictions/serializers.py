from rest_framework import serializers
from .models import Category, FortuneCookie, UserPrediction, FavoriteCookie


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']  # Список полей, которые будут включены в JSON


class FortuneCookieSerializer(serializers.ModelSerializer):
    """Сериализатор для предсказаний"""
    # Добавляем название категории как отдельное поле (удобно для API)
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = FortuneCookie
        fields = ['id', 'text', 'category', 'category_name', 'is_active', 'usage_count']


class UserPredictionSerializer(serializers.ModelSerializer):
    """Сериализатор для полученных предсказаний"""
    # Добавляем удобные поля из связанных объектов
    cookie_text = serializers.ReadOnlyField(source='cookie.text')
    cookie_category = serializers.ReadOnlyField(source='cookie.category.name')

    class Meta:
        model = UserPrediction
        fields = ['id', 'cookie', 'cookie_text', 'cookie_category', 'received_at', 'is_favorite']


class FavoriteCookieSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""
    cookie_text = serializers.ReadOnlyField(source='cookie.text')
    cookie_category = serializers.ReadOnlyField(source='cookie.category.name')

    class Meta:
        model = FavoriteCookie
        fields = ['id', 'cookie', 'cookie_text', 'cookie_category', 'added_at']
