import pytest
from django.core.exceptions import ValidationError  # для проверки, что ошибка действительно выбрасывается
from django.urls import reverse  # Превращает имя маршрута в URL-адрес
from predictions.models import FortuneCookie, Category, FavoriteCookie


@pytest.mark.django_db
class TestCookieValidation:
    """Валидация предсказаний (не пустые, минимум 5 символов)"""
    def test_empty_cookie_rejected(self, category):
        """Пустое предсказание нельзя сохранить"""
        cookie = FortuneCookie(text='', category=category)  # создаёт объект в памяти. привязываем к категории (из фикстуры)
        with pytest.raises(ValidationError):  # проверка, что код действительно выбрасывает ожидаемое исключение
            cookie.full_clean()  # вызывает все валидации модели

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
        # follow=True – если сервер вернёт редирект (код 302), то автоматически перейди по новому адресу
        response = auth_client.get(url, follow=True)

        # .exists() - Возвращает True, если такая запись есть, иначе False. Проверяем, что записи НЕТ
        assert FavoriteCookie.objects.filter(user=user, cookie=new_cookie).exists() == False
