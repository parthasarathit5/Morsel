from rest_framework import serializers

from .models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'name', 'emoji', 'is_veg', 'price', 'quantity', 'total')


class PaymentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('provider', 'razorpay_payment_id', 'amount', 'currency', 'status', 'demo', 'paid_at')


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSummarySerializer(read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_emoji = serializers.CharField(source='restaurant.emoji', read_only=True)
    delivery_minutes = serializers.IntegerField(source='restaurant.delivery_minutes', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'status',
            'restaurant_name',
            'restaurant_emoji',
            'delivery_minutes',
            'items',
            'payment',
            'items_total',
            'delivery_fee',
            'taxes',
            'grand_total',
            'delivery_name',
            'delivery_phone',
            'delivery_address',
            'created_at',
            'updated_at',
        )


class OrderListSerializer(serializers.ModelSerializer):
    """Compact serializer for the 'My Orders' page."""

    item_count = serializers.SerializerMethodField()
    first_items = serializers.SerializerMethodField()
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_emoji = serializers.CharField(source='restaurant.emoji', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'status',
            'restaurant_name',
            'restaurant_emoji',
            'item_count',
            'first_items',
            'grand_total',
            'created_at',
        )

    def get_item_count(self, obj: Order) -> int:
        return sum(item.quantity for item in obj.items.all())

    def get_first_items(self, obj: Order) -> str:
        names = [item.name for item in obj.items.all()[:3]]
        more = sum(item.quantity for item in obj.items.all()) - len(names)
        text = ', '.join(names)
        return f'{text} +{more} more' if more > 0 else text
