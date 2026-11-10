from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from restaurants.models import MenuItem, Restaurant


class Order(models.Model):
    """A food order placed by a user with a restaurant."""

    STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    STATUS_PLACED = 'placed'
    STATUS_PREPARING = 'preparing'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_AWAITING_PAYMENT, 'Awaiting payment'),
        (STATUS_PLACED, 'Order placed'),
        (STATUS_PREPARING, 'Preparing your food'),
        (STATUS_OUT_FOR_DELIVERY, 'Out for delivery'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    PROGRESSION = (STATUS_PLACED, STATUS_PREPARING, STATUS_OUT_FOR_DELIVERY, STATUS_DELIVERED)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name='orders')

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_AWAITING_PAYMENT)

    # Bill (all values in INR)
    items_total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    taxes = models.DecimalField(max_digits=6, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

    # Delivery details
    delivery_name = models.CharField(max_length=120)
    delivery_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'Order #{self.pk} — {self.user.email} @ {self.restaurant.name}'

    # -- bill helpers ------------------------------------------------------

    @staticmethod
    def compute_bill(items: list[dict[str, int]]) -> dict[str, Decimal]:
        """Compute bill server-side from DB prices. Never trust client prices.

        `items` is a list of {menu_item: <MenuItem>, quantity: int}.
        """
        items_total = sum(
            (item['menu_item'].price * item['quantity'] for item in items),
            Decimal('0.00'),
        )

        # Swiggy-style: free delivery above ₹149, else ₹29
        delivery_fee = Decimal('0.00') if items_total >= 149 else Decimal('29.00')

        # 5% GST + ₹6 platform fee
        taxes = (items_total * Decimal('0.05')).quantize(Decimal('0.01')) + Decimal('6.00')

        grand_total = items_total + delivery_fee + taxes
        return {
            'items_total': items_total,
            'delivery_fee': delivery_fee,
            'taxes': taxes,
            'grand_total': grand_total,
        }


class OrderItem(models.Model):
    """Denormalized snapshot of a menu item inside an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    emoji = models.CharField(max_length=8, default='🍛')
    is_veg = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def total(self) -> Decimal:
        return self.price * self.quantity

    def __str__(self) -> str:
        return f'{self.quantity} x {self.name}'


class Payment(models.Model):
    """Razorpay payment record for an order."""

    STATUS_CREATED = 'created'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = (
        (STATUS_CREATED, 'Created'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Failed'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    provider = models.CharField(max_length=30, default='razorpay')

    razorpay_order_id = models.CharField(max_length=64, blank=True)
    razorpay_payment_id = models.CharField(max_length=64, blank=True)

    amount = models.PositiveIntegerField(help_text='Amount in paise (INR x 100).')
    currency = models.CharField(max_length=8, default='INR')
    demo = models.BooleanField(default=False, help_text='True when paid in demo mode (no live keys).')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.provider}:{self.razorpay_order_id or "demo"} ({self.status})'

    @property
    def is_paid(self) -> bool:
        return self.status == self.STATUS_PAID


def razorpay_enabled() -> bool:
    return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)
