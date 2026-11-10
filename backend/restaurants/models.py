from django.db import models


class Restaurant(models.Model):
    """A restaurant / cloud kitchen listed on FoodFlow."""

    name = models.CharField(max_length=200)
    cuisine = models.CharField(max_length=120, help_text='e.g. "North Indian, Biryani"')
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    rating_count = models.PositiveIntegerField(default=100)
    delivery_minutes = models.PositiveIntegerField(default=30)
    price_for_two = models.PositiveIntegerField(default=300)
    address = models.CharField(max_length=300, blank=True)
    is_pure_veg = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    promoted = models.BooleanField(default=False)
    offer_text = models.CharField(max_length=120, blank=True)
    emoji = models.CharField(max_length=8, default='🍽️')
    gradient = models.CharField(
        max_length=120,
        default='linear-gradient(135deg, #f97316, #ef4444)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-promoted', '-rating', 'name')

    def __str__(self) -> str:
        return self.name


class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('order', 'name')
        verbose_name_plural = 'menu categories'

    def __str__(self) -> str:
        return f'{self.restaurant.name} — {self.name}'


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=400, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_veg = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    emoji = models.CharField(max_length=8, default='🍛')

    class Meta:
        ordering = ('-is_bestseller', 'name')

    def __str__(self) -> str:
        return f'{self.name} ({self.restaurant.name})'
