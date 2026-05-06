import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from predictions.models import FortuneCookie, Category, FavoriteCookie
from django.contrib.messages import get_messages


@pytest.mark.django_db
class TestCookieValidation:
    """Валидация предсказаний (не пустые, минимум 5 символов)"""
    def test_empty_cookie_rejected(self, category):
        """Пустое предсказание нельзя сохранить"""
        cookie = FortuneCookie(text='', category=category)
        with pytest.raises(ValidationError):
            cookie.full_clean()

    def test_short_cookie_rejected(self, category):
        """Короткое предсказание (меньше 5 символов) нельзя сохранить"""
        cookie = FortuneCookie(text='1234', category=category)
        with pytest.raises(ValidationError):
            cookie.full_clean()


@pytest.mark.django_db
class TestFavoritesLimit:
    """Лимит избранного (не больше 50)"""

    def test_cannot_add_51st_favorite(self, auth_client, user, category):
        """Нельзя добавить 51-е предсказание в избранное"""
        # Создаём 50 предсказаний
        for i in range(50):
            cookie = FortuneCookie.objects.create(text=f'Тест {i}', category=category)
            FavoriteCookie.objects.create(user=user, cookie=cookie)

        # Пытаемся добавить 51-е
        new_cookie = FortuneCookie.objects.create(text='51-е', category=category)
        url = reverse('add_to_favorites', args=[new_cookie.id])
        response = auth_client.get(url, follow=True)

        # Не добавилось
        assert FavoriteCookie.objects.filter(user=user, cookie=new_cookie).exists() == False