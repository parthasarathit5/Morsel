from django.contrib import admin

from .models import MenuCategory, MenuItem, Restaurant


class MenuCategoryInline(admin.TabularInline):
    model = MenuCategory
    extra = 0


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine', 'rating', 'is_open', 'promoted')
    list_filter = ('is_open', 'is_pure_veg', 'promoted')
    search_fields = ('name', 'cuisine')
    inlines = [MenuCategoryInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'is_veg', 'is_bestseller')
    list_filter = ('is_veg', 'is_bestseller', 'is_available')
    search_fields = ('name', 'restaurant__name')
