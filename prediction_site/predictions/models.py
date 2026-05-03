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