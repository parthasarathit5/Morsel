"""URL configuration for the Foodiebay backend."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('core.urls')),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/', include('restaurants.urls')),
    path('api/v1/', include('orders.urls')),
]
