from django.db import models


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
        on_delete=models.CASCADE,
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

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

class UserPrediction(models.Model):
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
    received_at = models.DateTimeField(auto_now_add=True, verbose_name="Получено")
    is_favorite = models.BooleanField(default=False, verbose_name="В избранном")

    class Meta:
        unique_together = ['user', 'cookie']
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