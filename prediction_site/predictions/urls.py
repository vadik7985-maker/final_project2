from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.home, name='home'),
    path('get/', views.get_prediction, name='get_prediction'),
    path('result/<int:prediction_id>/', views.prediction_result, name='prediction_result'),
    path('my-predictions/', views.my_predictions, name='my_predictions'),

    path('favorites/', views.favorites, name='favorites'),
    path('favorites/add/<int:cookie_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:cookie_id>/', views.remove_from_favorites, name='remove_from_favorites'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('top/', views.top_cookies, name='top_cookies'),

    # API-маршруты
    path('api/random/', api_views.api_random_cookie, name='api_random_cookie'),
    path('api/categories/', api_views.api_categories, name='api_categories'),
]