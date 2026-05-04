from django.shortcuts import render
from .models import Category, FortuneCookie


def home(request):
    categories = Category.objects.all()
    cookies_count = FortuneCookie.objects.count()
    categories_count = Category.objects.count()

    context = {
        'categories': categories,
        'cookies_count': cookies_count,
        'categories_count': categories_count,
    }

    return render(request, 'home.html', context)