import pytest
from django.urls import reverse
from predictions.models import FortuneCookie, Category


# ТЕСТЫ ДЛЯ API СЛУЧАЙНОГО ПРЕДСКАЗАНИЯ

@pytest.mark.django_db
class TestRandomCookieAPI:
    def test_api_random_cookie_returns_json(self, client, cookie):
        """API возвращает JSON с данными предсказания"""
        url = reverse('api_random_cookie')
        response = client.get(url)

        assert response.status_code == 200
        assert response.json()['text'] == cookie.text
        assert response.json()['category'] == cookie.category.name

    def test_api_random_cookie_no_cookies(self, client):
        """Если нет предсказаний - возвращает ошибку"""
        FortuneCookie.objects.all().delete()
        url = reverse('api_random_cookie')
        response = client.get(url)

        assert response.status_code == 404
        assert response.json()['error'] == 'Нет активных предсказаний'


# ТЕСТЫ ДЛЯ API КАТЕГОРИЙ

@pytest.mark.django_db
class TestCategoriesAPI:

    def test_api_categories_returns_list(self, client, category):
        """API возвращает список категорий"""
        url = reverse('api_categories')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['name'] == 'Любовь'

    def test_api_categories_multiple(self, client):
        """API возвращает все категории"""
        cat1 = Category.objects.create(name='Удача')
        cat2 = Category.objects.create(name='Карьера')

        url = reverse('api_categories')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.json()) == 2