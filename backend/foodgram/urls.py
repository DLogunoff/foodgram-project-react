from django.conf.urls import include
from django.urls import path

urlpatterns = [
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
]
