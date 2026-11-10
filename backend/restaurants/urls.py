from django.urls import path

from . import views

urlpatterns = [
    path('restaurants/cuisines/', views.CuisineListView.as_view(), name='cuisines'),
    path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('restaurants/', views.RestaurantListView.as_view(), name='restaurant-list'),
]
