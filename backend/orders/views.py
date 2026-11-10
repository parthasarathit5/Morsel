from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurants.models import MenuItem, Restaurant

from . import razorpay
from .models import Order, OrderItem, Payment, razorpay_enabled
from .serializers import OrderDetailSerializer, OrderListSerializer


class CheckoutView(APIView):
    """POST /api/v1/orders/checkout/

    Body:
    {
      "restaurant_id": 1,
      "items": [{"item_id": 10, "quantity": 2}, ...],
      "delivery": {"name": "...", "phone": "...", "address": "..."}
    }

    Creates the Order + items (prices taken from the DB) and a Razorpay
    order. Without Razorpay keys the response is flagged `demo_mode: true`
    and the frontend simulates payment.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        restaurant = Restaurant.objects.filter(pk=data.get('restaurant_id')).first()
        if restaurant is None:
            return Response({'detail': 'Restaurant not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not restaurant.is_open:
            return Response({'detail': 'This restaurant is currently closed.'}, status=status.HTTP_400_BAD_REQUEST)

        raw_items = data.get('items') or []
        if not isinstance(raw_items, list) or not raw_items:
            return Response({'detail': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Build validated item list from DB prices.
        menu_items: list[dict] = []
        for entry in raw_items:
            try:
                item_id = int(entry.get('item_id'))
                quantity = int(entry.get('quantity', 1))
            except (TypeError, ValueError):
                return Response({'detail': 'Invalid item payload.'}, status=status.HTTP_400_BAD_REQUEST)
            if quantity < 1 or quantity > 20:
                return Response({'detail': 'Quantity must be between 1 and 20.'}, status=status.HTTP_400_BAD_REQUEST)
            menu_item = MenuItem.objects.filter(pk=item_id, restaurant=restaurant).first()
            if menu_item is None:
                return Response(
                    {'detail': f'Item {item_id} does not belong to this restaurant.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not menu_item.is_available:
                return Response({'detail': f'{menu_item.name} is currently unavailable.'}, status=status.HTTP_400_BAD_REQUEST)
            menu_items.append({'menu_item': menu_item, 'quantity': quantity})

        delivery = data.get('delivery') or {}
        name = str(delivery.get('name', '')).strip()
        phone = str(delivery.get('phone', '')).strip()
        address = str(delivery.get('address', '')).strip()
        if not name or not phone or not address:
            return Response(
                {'detail': 'Delivery name, phone and address are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bill = Order.compute_bill(menu_items)
        order = Order.objects.create(
            user=request.user,
            restaurant=restaurant,
            status=Order.STATUS_AWAITING_PAYMENT,
            delivery_name=name,
            delivery_phone=phone,
            delivery_address=address,
            **bill,
        )
        for entry in menu_items:
            menu_item = entry['menu_item']
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                name=menu_item.name,
                emoji=menu_item.emoji,
                is_veg=menu_item.is_veg,
                price=menu_item.price,
                quantity=entry['quantity'],
            )

        amount_paise = int(order.grand_total * 100)
        payment = Payment.objects.create(order=order, amount=amount_paise)

        use_razorpay = razorpay_enabled()
        if use_razorpay:
            try:
                rp_order = razorpay.create_order(
                    amount_paise,
                    receipt=f'order_{order.pk}',
                    notes={'order_id': order.pk, 'restaurant': restaurant.name},
                )
                payment.razorpay_order_id = rp_order.get('id', '')
                payment.save(update_fields=['razorpay_order_id'])
            except razorpay.RazorpayError:
                # Keep the order but fall back to demo mode for this attempt.
                use_razorpay = False

        return Response(
            {
                'order_id': order.pk,
                'amount': float(order.grand_total),
                'amount_paise': amount_paise,
                'currency': 'INR',
                'demo_mode': not use_razorpay,
                'razorpay': {
                    'key_id': razorpay.settings.RAZORPAY_KEY_ID if use_razorpay else '',
                    'order_id': payment.razorpay_order_id,
                },
                'bill': {key: float(value) for key, value in bill.items()},
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyPaymentView(APIView):
    """POST /api/v1/orders/verify-payment/

    Body: {order_id, razorpay_order_id, razorpay_payment_id, razorpay_signature}
    Verifies the Razorpay Checkout signature and marks the order as placed.
    In demo mode (no keys configured) the payment is accepted as simulated.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        order = Order.objects.filter(
            pk=request.data.get('order_id'), user=request.user
        ).first()
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if order.payment.is_paid:
            return Response(OrderDetailSerializer(order).data)

        rp_order_id = str(request.data.get('razorpay_order_id', ''))
        rp_payment_id = str(request.data.get('razorpay_payment_id', ''))
        rp_signature = str(request.data.get('razorpay_signature', ''))

        if razorpay_enabled():
            if not rp_order_id or not rp_payment_id or not rp_signature:
                return Response({'detail': 'Missing Razorpay payment fields.'}, status=status.HTTP_400_BAD_REQUEST)
            if not razorpay.verify_checkout_signature(rp_order_id, rp_payment_id, rp_signature):
                order.payment.status = Payment.STATUS_FAILED
                order.payment.save(update_fields=['status'])
                return Response({'detail': 'Payment signature verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

        order.payment.status = Payment.STATUS_PAID
        order.payment.razorpay_payment_id = rp_payment_id or f'demo_{order.pk}'
        order.payment.demo = not razorpay_enabled()
        order.payment.paid_at = timezone.now()
        order.payment.save()
        order.status = Order.STATUS_PLACED
        order.save(update_fields=['status'])
        return Response(OrderDetailSerializer(order).data)


class RazorpayWebhookView(APIView):
    """POST /api/v1/payments/webhook/ — server-to-server confirmation.

    Configure in the Razorpay dashboard with event `payment.captured`.
    """

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        signature = request.headers.get('X-Razorpay-Signature', '')
        if not razorpay.verify_webhook_signature(request.body, signature):
            return Response({'detail': 'Invalid webhook signature.'}, status=status.HTTP_400_BAD_REQUEST)

        import json

        try:
            event = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'detail': 'Invalid payload.'}, status=status.HTTP_400_BAD_REQUEST)

        payload = event.get('payload', {})
        payment_entity = (payload.get('payment', {}).get('entity') or {})
        rp_order_id = payment_entity.get('order_id')
        if event.get('event') == 'payment.captured' and rp_order_id:
            payment = Payment.objects.filter(razorpay_order_id=rp_order_id).first()
            if payment and not payment.is_paid:
                payment.status = Payment.STATUS_PAID
                payment.razorpay_payment_id = payment_entity.get('id', '')
                payment.paid_at = timezone.now()
                payment.save()
                if payment.order.status == Order.STATUS_AWAITING_PAYMENT:
                    payment.order.status = Order.STATUS_PLACED
                    payment.order.save(update_fields=['status'])
        return Response({'detail': 'ok'})


class MyOrdersView(generics.ListAPIView):
    """GET /api/v1/orders/ — the signed-in user's orders, newest first."""

    permission_classes = [IsAuthenticated]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class AdvanceOrderView(APIView):
    """POST /api/v1/orders/<id>/advance/ — demo helper to move the order
    forward (placed → preparing → out for delivery → delivered)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = Order.objects.filter(pk=pk, user=request.user).first()
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if order.status not in Order.PROGRESSION:
            return Response({'detail': 'This order cannot be advanced.'}, status=status.HTTP_400_BAD_REQUEST)
        if order.status == Order.PROGRESSION[-1]:
            return Response({'detail': 'Order already delivered.'}, status=status.HTTP_400_BAD_REQUEST)
        next_index = Order.PROGRESSION.index(order.status) + 1
        order.status = Order.PROGRESSION[next_index]
        order.save(update_fields=['status'])
        return Response(OrderDetailSerializer(order).data)


class CancelOrderView(APIView):
    """POST /api/v1/orders/<id>/cancel/ — cancel while food is not yet cooked."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = Order.objects.filter(pk=pk, user=request.user).first()
        if order is None:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if order.status in (Order.STATUS_DELIVERED, Order.STATUS_CANCELLED, Order.STATUS_OUT_FOR_DELIVERY):
            return Response({'detail': 'This order can no longer be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status'])
        return Response(OrderDetailSerializer(order).data)
