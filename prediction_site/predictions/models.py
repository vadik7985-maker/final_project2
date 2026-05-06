from django.db import models
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class FortuneCookie(models.Model):
    text = models.TextField(verbose_name="Текст предсказания")
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE, #удалятся все
        related_name='cookies',
        verbose_name="Категория"
    )
    created_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Создано пользователем"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Количество использований")

    def clean(self): # не может быть пустым или коротким
        if not self.text or not self.text.strip():
            raise ValidationError({'text': 'Текст предсказания не может быть пустым'})

        if len(self.text.strip()) < 5:
            raise ValidationError({'text': 'Предсказание должно содержать минимум 5 символов'})

    def __str__(self):
        return self.text[:50] + "..." if len(self.text) > 50 else self.text

    class Meta:
        verbose_name = "Печенье с предсказанием"
        verbose_name_plural = "Печеньки с предсказаниями"


class UserProfile(models.Model):
    user = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    bio = models.TextField(blank=True, verbose_name="О себе")
    favorite_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Любимая категория"
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name="Аватар"
    )

    def __str__(self):
        return f"Профиль {self.user.username}" #объект превр в строку

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

class UserPrediction(models.Model):
    user = models.ForeignKey( # предсказ с конкр польз
        'users.CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    cookie = models.ForeignKey( #с конкр предсказ
        FortuneCookie,
        on_delete=models.CASCADE,
        verbose_name="Предсказание"
    )
    received_at = models.DateTimeField(auto_now_add=True, verbose_name="Получено")
    is_favorite = models.BooleanField(default=False, verbose_name="В избранном")

    class Meta:
        unique_together = ['user', 'cookie'] #нельзя получить дважды
        verbose_name = "Полученное предсказание"
        verbose_name_plural = "Полученные предсказания"

    def __str__(self):
        return f"{self.user.username} - {self.cookie.text[:30]}..."


class FavoriteCookie(models.Model):
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    cookie = models.ForeignKey(
        FortuneCookie,
        on_delete=models.CASCADE,
        verbose_name="Предсказание"
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        unique_together = ['user', 'cookie']
        verbose_name = "Избранное предсказание"
        verbose_name_plural = "Избранные предсказания"

    def __str__(self):
        return f"Избранное: {self.user.username} - {self.cookie.text[:30]}..."


class Achievement(models.Model):
    """Достижение, которое может получить пользователь"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    icon = models.CharField(max_length=50, default='🏆', verbose_name="Иконка")

    # Условия получения
    required_predictions = models.PositiveIntegerField(default=0, verbose_name="Требуется предсказаний")
    required_favorites = models.PositiveIntegerField(default=0, verbose_name="Требуется в избранном")
    required_category_count = models.PositiveIntegerField(default=0, verbose_name="Требуется уникальных категорий")

    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        ordering = ['order']
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"

    def __str__(self):
        return f"{self.icon} {self.name}"


class UserAchievement(models.Model):
    """Связь пользователя с полученными достижениями"""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name="Пользователь")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, verbose_name="Достижение")
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name="Получено")

    class Meta:
        unique_together = ['user', 'achievement']
        verbose_name = "Достижение пользователя"
        verbose_name_plural = "Достижения пользователей"

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"