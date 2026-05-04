from django.urls import include
from django.contrib import admin
from django.urls import path
from users.views import register

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('django.contrib.auth.urls')),
    path('auth/register/', register, name='register'),

    path('', include('predictions.urls')),
]
