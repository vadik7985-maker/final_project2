from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, FortuneCookie, UserPrediction, FavoriteCookie
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
    
    context = {
        'prediction': user_prediction,
        'cookie': user_prediction.cookie,
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

    favorite, created = FavoriteCookie.objects.get_or_create(
        user=request.user,
        cookie=cookie
    )

    if created:
        messages.success(request, f'Предсказание добавлено в избранное ❤️')
    else:
        messages.info(request, 'Это предсказание уже в избранном')

    return redirect('prediction_result', prediction_id=request.GET.get('prediction_id'))


@login_required
def remove_from_favorites(request, cookie_id):
    cookie = get_object_or_404(FortuneCookie, id=cookie_id)
    FavoriteCookie.objects.filter(user=request.user, cookie=cookie).delete()

    messages.success(request, 'Предсказание удалено из избранного')
    return redirect('favorites')


@login_required
def favorites(request):
    favorite_cookies = FavoriteCookie.objects.filter(
        user=request.user
    ).select_related('cookie').order_by('-added_at')

    context = {
        'favorite_cookies': favorite_cookies,
    }
    return render(request, 'predictions/favorites.html', context)