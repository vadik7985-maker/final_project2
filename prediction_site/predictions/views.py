from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, FortuneCookie, UserPrediction, FavoriteCookie, UserProfile, Achievement, UserAchievement
import random
from .forms import UserProfileForm
import logging

logger = logging.getLogger(__name__)


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
    # Информационное сообщение: кто запросил предсказание
    logger.info(f"Пользователь {request.user.username} запросил предсказание")

    active_cookies = FortuneCookie.objects.filter(is_active=True)

    if not active_cookies.exists():
        logger.warning("Активных предсказаний нет!")
        messages.warning(request, 'К сожалению, активных предсказаний пока нет. Загляните позже!')
        return redirect('home')

    # Получаем ID предсказаний, которые пользователь уже получал
    received_cookies_ids = UserPrediction.objects.filter(
        user=request.user
    ).values_list('cookie_id', flat=True)

    # Исключаем их из выбора
    available_cookies = active_cookies.exclude(id__in=received_cookies_ids)

    # Если все предсказания уже получены
    if not available_cookies.exists():
        logger.info(f"Пользователь {request.user.username} уже получил все предсказания")
        messages.warning(request, 'Вы уже получили все возможные предсказания! 🎉')
        return redirect('my_predictions')

    cookie = random.choice(available_cookies)

    cookie.usage_count += 1
    cookie.save()

    # Отладочное сообщение: какое предсказание выбрано (видно только при уровне DEBUG)
    logger.debug(f"Выдано предсказание id={cookie.id}, текст={cookie.text[:30]}...")

    user_prediction = UserPrediction.objects.create(
        user=request.user,
        cookie=cookie
    )

    logger.info(f"Предсказание сохранено, id={user_prediction.id}")

    # Проверяем и выдаём достижения
    new_achievements = check_and_award_achievements(request.user)
    if new_achievements:
        for ach in new_achievements:
            logger.info(f"Пользователь {request.user.username} получил достижение: {ach.icon} {ach.name}")
            messages.success(request, f'Получено достижение: {ach.icon} {ach.name}!')

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


@login_required #авторизован ли
def add_to_favorites(request, cookie_id):
    cookie = get_object_or_404(FortuneCookie, id=cookie_id)
    prediction_id = request.GET.get('prediction_id')

    favorites_count = FavoriteCookie.objects.filter(user=request.user).count()

    if favorites_count >= 50: #нельзя больше 50 добавить в избр
        messages.error(request, 'Нельзя добавить больше 50 предсказаний в избранное!')
        if prediction_id:
            return redirect('prediction_result', prediction_id=prediction_id)
        return redirect('favorites')

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
    return render(request, 'favorite.html', context)


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user) #либо созд новую, либо находим сущ

    predictions_count = UserPrediction.objects.filter(user=request.user).count()
    favorites_count = FavoriteCookie.objects.filter(user=request.user).count()

    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')

    context = {
        'user_profile': user_profile,
        'predictions_count': predictions_count,
        'favorites_count': favorites_count,
        'total_cookies': FortuneCookie.objects.count(),
        'user_achievements': user_achievements,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'edit_profile.html', context)


def top_cookies(request):
    top_list = FortuneCookie.objects.filter(is_active=True).order_by('-usage_count')[:10]
    context = {
        'top_cookies': top_list,
    }
    return render(request, 'top_cookies.html', context)


def check_and_award_achievements(user):
    """Проверяет и выдает достижения пользователю"""
    predictions_count = UserPrediction.objects.filter(user=user).count()
    favorites_count = FavoriteCookie.objects.filter(user=user).count()

    # Получаем количество уникальных категорий в предсказаниях пользователя
    unique_categories = UserPrediction.objects.filter(
        user=user
    ).values_list('cookie__category', flat=True).distinct().count()

    # Все активные достижения
    achievements = Achievement.objects.filter(is_active=True)

    awarded = []
    for ach in achievements:
        # Проверяем, не получил ли уже пользователь это достижение
        if UserAchievement.objects.filter(user=user, achievement=ach).exists():
            continue

        # Проверяем условия
        conditions_met = True
        if ach.required_predictions > 0 and predictions_count < ach.required_predictions:
            conditions_met = False
        if ach.required_favorites > 0 and favorites_count < ach.required_favorites:
            conditions_met = False
        if ach.required_category_count > 0 and unique_categories < ach.required_category_count:
            conditions_met = False

        if conditions_met:
            UserAchievement.objects.create(user=user, achievement=ach)
            awarded.append(ach)

    return awarded