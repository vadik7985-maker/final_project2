import pytest
from django.db import IntegrityError
from predictions.models import Category, FortuneCookie, UserProfile, UserPrediction, FavoriteCookie, Achievement, UserAchievement
from django.contrib.auth import get_user_model

User = get_user_model()


# ТЕСТЫ ДЛЯ МОДЕЛИ CATEGORY (Категория)

@pytest.mark.django_db
class TestCategory:
    def test_create_category(self, category):
        """
        Тест создания категории
        Проверяет: объект создаётся, поля заполняются правильно
        """
        assert category.name == 'Любовь'
        assert category.description == 'Предсказания о любви и отношениях'

    def test_category_str(self, category):
        """
        Тест строкового представления категории
        Проверяет: метод __str__ возвращает название категории
        """
        assert str(category) == 'Любовь'

    def test_category_verbose_names(self):
        """
        Тест русских названий полей (verbose_name)
        Проверяет: в админке поля подписаны правильно
        """
        name_field = Category._meta.get_field('name')
        description_field = Category._meta.get_field('description')

        assert name_field.verbose_name == 'Название'
        assert description_field.verbose_name == 'Описание'


# ТЕСТЫ ДЛЯ МОДЕЛИ FORTUNECOOKIE (Предсказание)

@pytest.mark.django_db
class TestFortuneCookie:
    def test_create_cookie(self, cookie, category):
        """
        Тест создания предсказания
        Проверяет: объект создаётся, поля заполняются, usage_count по умолчанию = 0
        """
        assert cookie.text == 'Вас ждёт прекрасный день!'
        assert cookie.category == category
        assert cookie.is_active == True
        assert cookie.usage_count == 0  # по умолчанию ноль

    def test_cookie_str_short_text(self, category):
        """
        Тест __str__ для короткого текста (меньше 50 символов)
        Проверяет: возвращается весь текст, без обрезания
        """
        short_text = 'Короткое предсказание'
        cookie = FortuneCookie.objects.create(
            text=short_text,
            category=category,
            is_active=True
        )
        assert str(cookie) == short_text

    def test_cookie_str_long_text(self, category):
        """
        Тест __str__ для длинного текста (больше 50 символов)
        Проверяет: текст обрезается до 50 символов и добавляется ...
        """
        long_text = 'А' * 60  # 60 символов "А"
        cookie = FortuneCookie.objects.create(
            text=long_text,
            category=category,
            is_active=True
        )
        # Должно быть 50 символов + "..."
        assert str(cookie) == 'А' * 50 + '...'

    def test_cookie_category_relationship(self, cookie, category):
        """
        Тест связи с категорией (ForeignKey, связь 1:N)
        Проверяет: у предсказания есть категория, у категории есть список предсказаний
        """
        # Прямая связь: предсказание - категория
        assert cookie.category == category

        # Обратная связь: категория - список предсказаний (related_name='cookies')
        assert category.cookies.count() == 1
        assert category.cookies.first() == cookie

    def test_cookie_is_active_default(self, category):
        """
        Тест значения по умолчанию для поля is_active
        Проверяет: если не указать is_active, становится True (из модели)
        """
        cookie = FortuneCookie.objects.create(
            text='Предсказание без указания is_active',
            category=category
        )
        assert cookie.is_active == True  # default=True из модели

