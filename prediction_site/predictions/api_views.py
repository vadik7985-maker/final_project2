from django.http import JsonResponse
from .models import FortuneCookie, Category
import random

def api_random_cookie(request):
    """Отдаёт случайное активное предсказание в JSON"""
    active = FortuneCookie.objects.filter(is_active=True)
    if not active.exists():
        return JsonResponse({'error': 'Нет активных предсказаний'}, status=404)

    cookie = random.choice(active)
    data = {
        'id': cookie.id,
        'text': cookie.text,
        'category': cookie.category.name,
        'usage_count': cookie.usage_count,
    }
    return JsonResponse(data)

def api_categories(request):
    """Возвращает список всех категорий"""
    categories = Category.objects.all().values('id', 'name', 'description')
    return JsonResponse(list(categories), safe=False)


# DRF API VIEWS

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, FortuneCookie, UserPrediction, FavoriteCookie
from .serializers import (
    CategorySerializer,
    FortuneCookieSerializer,
    UserPredictionSerializer,
    FavoriteCookieSerializer
)


@api_view(['GET'])
def drf_categories(request):
    """API: список всех категорий"""
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def drf_random_cookie(request):
    """API: случайное активное предсказание"""
    active_cookies = FortuneCookie.objects.filter(is_active=True)

    if not active_cookies.exists():
        return Response(
            {'error': 'Нет активных предсказаний'},
            status=status.HTTP_404_NOT_FOUND
        )

    import random
    cookie = random.choice(active_cookies)
    serializer = FortuneCookieSerializer(cookie)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@login_required
def drf_my_predictions(request):
    """API: мои полученные предсказания"""
    if request.method == 'GET':
        predictions = UserPrediction.objects.filter(user=request.user).order_by('-received_at')
        serializer = UserPredictionSerializer(predictions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Получить новое предсказание
        active_cookies = FortuneCookie.objects.filter(is_active=True)
        received_ids = UserPrediction.objects.filter(user=request.user).values_list('cookie_id', flat=True)
        available = active_cookies.exclude(id__in=received_ids)

        if not available.exists():
            return Response(
                {'error': 'У вас уже есть все предсказания'},
                status=status.HTTP_400_BAD_REQUEST
            )

        import random
        cookie = random.choice(available)
        prediction = UserPrediction.objects.create(user=request.user, cookie=cookie)
        serializer = UserPredictionSerializer(prediction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@login_required
def drf_my_favorites(request):
    """API: мои избранные предсказания"""
    favorites = FavoriteCookie.objects.filter(user=request.user).order_by('-added_at')
    serializer = FavoriteCookieSerializer(favorites, many=True)
    return Response(serializer.data)


@api_view(['POST', 'DELETE'])
@login_required
def drf_favorite_toggle(request, cookie_id):
    """API: добавить/удалить из избранного"""
    cookie = get_object_or_404(FortuneCookie, id=cookie_id)
    favorite = FavoriteCookie.objects.filter(user=request.user, cookie=cookie)

    if request.method == 'POST':
        if favorite.exists():
            return Response(
                {'message': 'Уже в избранном'},
                status=status.HTTP_200_OK
            )

        # Проверка лимита 50
        if FavoriteCookie.objects.filter(user=request.user).count() >= 50:
            return Response(
                {'error': 'Нельзя добавить больше 50 предсказаний в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )

        FavoriteCookie.objects.create(user=request.user, cookie=cookie)
        return Response(
            {'message': 'Добавлено в избранное'},
            status=status.HTTP_201_CREATED
        )

    elif request.method == 'DELETE':
        if not favorite.exists():
            return Response(
                {'message': 'Не в избранном'},
                status=status.HTTP_200_OK
            )

        favorite.delete()
        return Response(
            {'message': 'Удалено из избранного'},
            status=status.HTTP_200_OK
        )