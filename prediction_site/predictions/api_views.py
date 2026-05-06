from django.http import JsonResponse
from .models import FortuneCookie, Category
import random

def api_random_cookie(request):
    """Отдаёт случайное активное предсказание в JSON"""
    active = FortuneCookie.objects.filter(is_active=True)
    if not active.exists():
        return JsonResponse({'error': 'Нет активных предсказаний'}, status=404)

    cookie = random.choice(active)
    data = {
        'id': cookie.id,
        'text': cookie.text,
        'category': cookie.category.name,
        'usage_count': cookie.usage_count,
    }
    return JsonResponse(data)

def api_categories(request):
    """Возвращает список всех категорий"""
    categories = Category.objects.all().values('id', 'name', 'description')
    return JsonResponse(list(categories), safe=False)