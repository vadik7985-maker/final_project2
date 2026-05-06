# Фикстуры для тестирования проекта

import pytest
from django.contrib.auth import get_user_model
from predictions.models import Category, FortuneCookie, UserProfile

# Получаем модель пользователя (она кастомная, из users.models)
User = get_user_model()


@pytest.fixture
def user():
    """Фикстура: создаёт тестового пользователя"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def user2():
    """Фикстура: создаёт второго тестового пользователя"""
    return User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )


@pytest.fixture
def category():
    """Фикстура: создаёт тестовую категорию"""
    return Category.objects.create(
        name='Любовь',
        description='Предсказания о любви и отношениях'
    )


@pytest.fixture
def cookie(category):
    """Фикстура: создаёт тестовое предсказание (печеньку)"""
    return FortuneCookie.objects.create(
        text='Вас ждёт прекрасный день!',
        category=category,
        is_active=True  # активное, пользователи могут его получить
    )


@pytest.fixture
def user_profile(user):
    """Фикстура: создаёт профиль пользователя (связь 1:1)"""
    profile, created = UserProfile.objects.get_or_create(user=user)  # ищет профиль пользователя, если его нет создает
    # True – если объект был создан сейчас, False – если найдён существующий
    return profile


@pytest.fixture
def auth_client(client, user):  # имитация браузера
    """Фикстура: возвращает авторизованного клиента (уже залогинен)"""
    client.force_login(user)
    return client
