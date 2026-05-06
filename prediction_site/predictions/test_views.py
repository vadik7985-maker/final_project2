import pytest
from django.urls import reverse
from predictions.models import FortuneCookie, UserPrediction


@pytest.mark.django_db
class TestHomeView:
    """Главная страница"""

    def test_home_page_available(self, client):
        """Главная страница доступна всем"""
        url = reverse('home')
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestGetPredictionView:
    """Получение предсказания"""

    def test_anonymous_redirected_to_login(self, client):
        """Аноним перенаправляется на страницу логина"""
        url = reverse('get_prediction')
        response = client.get(url)
        assert response.status_code == 302  # редирект


@pytest.mark.django_db
class TestProfileView:
    """Страница профиля"""

    def test_anonymous_redirected_to_login(self, client):
        """Аноним не видит профиль"""
        url = reverse('profile')
        response = client.get(url)
        assert response.status_code == 302

    def test_authenticated_can_view_profile(self, auth_client):
        """Авторизованный видит профиль"""
        url = reverse('profile')
        response = auth_client.get(url)
        assert response.status_code == 200