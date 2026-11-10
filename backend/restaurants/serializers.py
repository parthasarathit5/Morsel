from rest_framework import serializers

from .models import MenuCategory, MenuItem, Restaurant


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = MenuItem
        fields = (
            'id',
            'name',
            'description',
            'price',
            'is_veg',
            'is_bestseller',
            'is_available',
            'emoji',
            'category',
        )


class MenuCategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ('id', 'name', 'items')


class RestaurantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'id',
            'name',
            'cuisine',
            'rating',
            'rating_count',
            'delivery_minutes',
            'price_for_two',
            'is_pure_veg',
            'is_open',
            'promoted',
            'offer_text',
            'emoji',
            'gradient',
        )


class RestaurantDetailSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = RestaurantListSerializer.Meta.fields + ('address', 'categories')
