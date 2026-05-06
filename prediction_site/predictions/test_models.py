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


# ТЕСТЫ ДЛЯ МОДЕЛИ USERPROFILE (Профиль пользователя, связь 1:1)

@pytest.mark.django_db
class TestUserProfile:
    def test_profile_created(self, user_profile, user):
        """
        Тест: профиль создаётся и связан с пользователем
        Проверяет связь 1:1 – у пользователя есть профиль
        """
        assert user_profile.user == user
        assert user_profile.bio == ''  # по умолчанию пустая строка

    def test_profile_str(self, user_profile, user):
        """
        Тест строкового представления профиля
        Проверяет: __str__ возвращает "Профиль {username}"
        """
        assert str(user_profile) == f'Профиль {user.username}'

    def test_profile_one_to_one_unique(self, user):
        """
        Тест: get_or_create не создаёт дубликаты профиля
        Проверяет: при многократном вызове get_or_create создаётся только один профиль
        """
        # Первый вызов - создаёт профиль
        profile1, created1 = UserProfile.objects.get_or_create(user=user)
        assert created1 == True  # был создан

        # Второй вызов - находит существующий
        profile2, created2 = UserProfile.objects.get_or_create(user=user)
        assert created2 == False  # НЕ был создан, а найден

        # Проверяем, что оба раза вернулся один и тот же профиль
        assert profile1.id == profile2.id
        assert UserProfile.objects.filter(user=user).count() == 1


# ТЕСТЫ ДЛЯ МОДЕЛИ USERPREDICTION (Полученные предсказания)

@pytest.mark.django_db
class TestUserPrediction:
    def test_create_user_prediction(self, user, cookie):
        """
        Тест создания записи о полученном предсказании
        Проверяет: запись создаётся, is_favorite по умолчанию False
        """
        prediction = UserPrediction.objects.create(
            user=user,
            cookie=cookie
        )
        assert prediction.user == user
        assert prediction.cookie == cookie
        assert prediction.is_favorite == False

    def test_user_prediction_str(self, user, cookie):
        """
        Тест строкового представления
        Проверяет: __str__ возвращает "username - текст предсказания"
        """
        prediction = UserPrediction.objects.create(user=user, cookie=cookie)
        expected = f"{user.username} - {cookie.text[:30]}..."
        assert str(prediction) == expected

    def test_unique_together_user_cookie(self, user, cookie):
        """
        Тест: пользователь не может получить одно предсказание дважды
        Проверяет unique_together = ['user', 'cookie']
        """
        # Первая запись – создаётся
        UserPrediction.objects.create(user=user, cookie=cookie)

        # Вторая запись с тем же пользователем и предсказанием – должна вызвать ошибку
        with pytest.raises(IntegrityError):
            UserPrediction.objects.create(user=user, cookie=cookie)


# ТЕСТЫ ДЛЯ МОДЕЛИ FAVORITECOOKIE (Избранное)

@pytest.mark.django_db
class TestFavoriteCookie:
    def test_add_to_favorites(self, user, cookie):
        """
        Тест добавления в избранное
        Проверяет: запись создаётся корректно
        """
        favorite = FavoriteCookie.objects.create(
            user=user,
            cookie=cookie
        )
        assert favorite.user == user
        assert favorite.cookie == cookie

    def test_favorite_str(self, user, cookie):
        """
        Тест строкового представления избранного
        Проверяет: __str__ возвращает "Избранное: username - текст"
        """
        favorite = FavoriteCookie.objects.create(user=user, cookie=cookie)
        expected = f"Избранное: {user.username} - {cookie.text[:30]}..."
        assert str(favorite) == expected

    def test_unique_favorite(self, user, cookie):
        """
        Тест: нельзя дважды добавить одно предсказание в избранное
        Проверяет unique_together = ['user', 'cookie']
        """
        FavoriteCookie.objects.create(user=user, cookie=cookie)

        with pytest.raises(IntegrityError):
            FavoriteCookie.objects.create(user=user, cookie=cookie)


# ТЕСТЫ ДЛЯ МОДЕЛИ ACHIEVEMENT (Достижения, связь N:N)

@pytest.mark.django_db
class TestAchievement:
    def test_create_achievement(self):
        """
        Тест создания достижения
        Проверяет: поля заполняются, __str__ возвращает иконку и название
        """
        achievement = Achievement.objects.create(
            name='Первый раз',
            description='Получить первое предсказание',
            icon='🎉',
            required_predictions=1
        )
        assert achievement.name == 'Первый раз'
        assert achievement.icon == '🎉'
        assert str(achievement) == '🎉 Первый раз'

    def test_user_achievement_relationship(self, user):
        """
        Тест связи N:N между пользователем и достижением
        Проверяет: можно связать пользователя с достижением
        """
        achievement = Achievement.objects.create(
            name='Тестовое достижение',
            description='Для теста',
            required_predictions=1
        )

        # Создаём связь
        user_achievement = UserAchievement.objects.create(
            user=user,
            achievement=achievement
        )

        # Проверяем прямую связь
        assert user_achievement.user == user
        assert user_achievement.achievement == achievement

        # Проверяем обратные связи
        assert user.userachievement_set.count() == 1
        assert achievement.userachievement_set.count() == 1

    def test_unique_user_achievement(self, user):
        """
        Тест: одно достижение нельзя получить дважды
        Проверяет unique_together = ['user', 'achievement']
        """
        achievement = Achievement.objects.create(
            name='Уникальное достижение',
            description='Нельзя получить дважды'
        )

        UserAchievement.objects.create(user=user, achievement=achievement)

        with pytest.raises(IntegrityError):
            UserAchievement.objects.create(user=user, achievement=achievement)

    def test_achievement_ordering(self):
        """
        Тест сортировки достижений по полю order
        Проверяет: class Meta: ordering = ['order']
        """
        achiev1 = Achievement.objects.create(name='Первое', order=2)
        achiev2 = Achievement.objects.create(name='Второе', order=1)

        # Должны быть отсортированы по order (меньший порядок – первый)
        achievements = Achievement.objects.all()
        assert achievements[0].name == 'Второе'  # order=1
        assert achievements[1].name == 'Первое'  # order=2