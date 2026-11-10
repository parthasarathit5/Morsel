from rest_framework import generics
from rest_framework.response import Response

from .models import Restaurant
from .serializers import RestaurantDetailSerializer, RestaurantListSerializer


class RestaurantListView(generics.ListAPIView):
    """GET /api/v1/restaurants/?search=&cuisine=&veg=1&open=1&sort=rating"""

    serializer_class = RestaurantListSerializer

    def get_queryset(self):
        queryset = Restaurant.objects.all()

        params = self.request.query_params
        search = params.get('search')
        if search:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(name__icontains=search) | Q(cuisine__icontains=search)
            )

        cuisine = params.get('cuisine')
        if cuisine:
            queryset = queryset.filter(cuisine__icontains=cuisine)

        if params.get('veg') in ('1', 'true'):
            queryset = queryset.filter(is_pure_veg=True)

        if params.get('open') in ('1', 'true'):
            queryset = queryset.filter(is_open=True)

        sort = params.get('sort')
        if sort == 'delivery_time':
            queryset = queryset.order_by('delivery_minutes', '-rating')
        elif sort == 'rating':
            queryset = queryset.order_by('-promoted', '-rating')

        return queryset


class RestaurantDetailView(generics.RetrieveAPIView):
    queryset = Restaurant.objects.prefetch_related('categories__items')
    serializer_class = RestaurantDetailSerializer


class CuisineListView(generics.ListAPIView):
    """Distinct cuisine strings for the home page filter chips."""

    def list(self, request, *args, **kwargs):
        cuisines = sorted(
            {c.strip() for r in Restaurant.objects.values_list('cuisine', flat=True) for c in r.split(',')}
        )
        return Response({'count': len(cuisines), 'results': cuisines})
