from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),          
    path('get/', views.get_prediction, name='get_prediction'),
    path('result/<int:prediction_id>/', views.prediction_result, name='prediction_result'),
]