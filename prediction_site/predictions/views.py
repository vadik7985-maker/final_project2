from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, FortuneCookie, UserPrediction, FavoriteCookie, UserProfile
import random


def home(request):
    categories = Category.objects.all()
    cookies_count = FortuneCookie.objects.count()
    categories_count = Category.objects.count()

    context = {
        'categories': categories,
        'cookies_count': cookies_count,
        'categories_count': categories_count,
    }

    return render(request, 'home.html', context)


@login_required
def get_prediction(request):
    active_cookies = FortuneCookie.objects.filter(is_active=True)
    
    if not active_cookies.exists():
        messages.warning(request, 'К сожалению, активных предсказаний пока нет. Загляните позже!')
        return redirect('home')
    
    cookie = random.choice(active_cookies)
    
    cookie.usage_count += 1
    cookie.save()
    
    user_prediction = UserPrediction.objects.create(
        user=request.user,
        cookie=cookie
    )
    
    return redirect('prediction_result', prediction_id=user_prediction.id)


@login_required
def prediction_result(request, prediction_id):
    user_prediction = get_object_or_404(
        UserPrediction, 
        id=prediction_id, 
        user=request.user
    )
    
    # Проверяем, есть ли предсказание в избранном
    is_favorite = FavoriteCookie.objects.filter(
        user=request.user, 
        cookie=user_prediction.cookie
    ).exists()
    
    context = {
        'prediction': user_prediction,
        'cookie': user_prediction.cookie,
        'is_favorite': is_favorite,
    }
    
    return render(request, 'result.html', context)


@login_required
def my_predictions(request):
    predictions_list = UserPrediction.objects.filter(
        user=request.user
    ).order_by('-received_at') 
    
    context = {
        'predictions_list': predictions_list,
        'total_count': predictions_list.count(),
    }
    
    return render(request, 'my_predictions.html', context)


@login_required
def add_to_favorites(request, cookie_id):
    cookie = get_object_or_404(FortuneCookie, id=cookie_id)
    prediction_id = request.GET.get('prediction_id')

    favorite, created = FavoriteCookie.objects.get_or_create(
        user=request.user,
        cookie=cookie
    )

    if created:
        messages.success(request, 'Предсказание добавлено в избранное')
    else:
        messages.info(request, 'Это предсказание уже в избранном')

    if prediction_id:
        return redirect('prediction_result', prediction_id=prediction_id)
    return redirect('favorites')


@login_required
def remove_from_favorites(request, cookie_id):
    cookie = get_object_or_404(FortuneCookie, id=cookie_id)
    FavoriteCookie.objects.filter(user=request.user, cookie=cookie).delete()

    messages.success(request, 'Предсказание удалено из избранного')
    return redirect('favorites')


@login_required
def favorites(request):
    favorite_list = FavoriteCookie.objects.filter(
        user=request.user
    ).select_related('cookie', 'cookie__category').order_by('-added_at')

    context = {
        'favorite_list': favorite_list,
    }
    return render(request, 'favorites.html', context)


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    predictions_count = UserPrediction.objects.filter(user=request.user).count()
    favorites_count = FavoriteCookie.objects.filter(user=request.user).count()

    context = {
        'user_profile': user_profile,
        'predictions_count': predictions_count,
        'favorites_count': favorites_count,
        'total_cookies': FortuneCookie.objects.count(),
    }
    return render(request, 'profile.html', context)