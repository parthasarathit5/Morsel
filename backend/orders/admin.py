from django.contrib import admin

from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('name', 'emoji', 'is_veg', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'status', 'grand_total', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'restaurant__name', 'delivery_name')
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'provider', 'razorpay_order_id', 'razorpay_payment_id', 'amount', 'status', 'demo')
    list_filter = ('status', 'demo', 'provider')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id')
