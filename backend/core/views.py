"""Core API views: health check and API index."""

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

SERVICE_NAME = 'Foodiebay-backend'


@api_view(['GET'])
def health(request):
    """Liveness probe."""
    return Response({'status': 'ok', 'service': SERVICE_NAME})


@api_view(['GET'])
def api_index(request):
    """JSON index of the available API endpoints."""
    return Response(
        {
            'name': 'Foodiebay API',
            'version': 'v1',
            'service': SERVICE_NAME,
            'docs': {
                'restaurants': '/api/v1/restaurants/',
                'restaurant detail': '/api/v1/restaurants/{id}/',
                'cuisines': '/api/v1/restaurants/cuisines/',
                'register (POST)': '/api/v1/auth/register/',
                'login token (POST)': '/api/v1/auth/token/',
                'refresh token (POST)': '/api/v1/auth/token/refresh/',
                'me': '/api/v1/auth/me/',
                'checkout (POST)': '/api/v1/orders/checkout/',
                'verify payment (POST)': '/api/v1/orders/verify-payment/',
                'my orders': '/api/v1/orders/',
                'order detail': '/api/v1/orders/{id}/',
                'advance order (POST)': '/api/v1/orders/{id}/advance/',
                'cancel order (POST)': '/api/v1/orders/{id}/cancel/',
                'razorpay webhook (POST)': '/api/v1/payments/webhook/',
                'admin': '/admin/',
            },
            'payments': 'demo' if not (settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET) else 'razorpay',
        }
    )
