"""API tests for the Foodiebay order + payment flow."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from orders.models import Order, Payment
from restaurants.models import MenuItem, Restaurant

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(email='t@example.com', password='secret123', first_name='Test')


@pytest.fixture
def auth(user):
    client = APIClient()
    response = client.post(
        '/api/v1/auth/token/', {'email': 't@example.com', 'password': 'secret123'}, format='json'
    )
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return client


@pytest.fixture
def restaurant():
    restaurant = Restaurant.objects.create(
        name='Test Kitchen', cuisine='Test', rating='4.5', delivery_minutes=20
    )
    from restaurants.models import MenuCategory

    category = MenuCategory.objects.create(restaurant=restaurant, name='Main')
    MenuItem.objects.create(
        restaurant=restaurant, category=category, name='Test Dish', price=100
    )
    return restaurant


def test_restaurant_list_and_detail(auth, restaurant):
    response = auth.get('/api/v1/restaurants/')
    assert response.status_code == 200
    assert response.data['results'][0]['name'] == 'Test Kitchen'

    detail = auth.get(f'/api/v1/restaurants/{restaurant.pk}/')
    assert detail.status_code == 200
    assert detail.data['categories'][0]['items'][0]['name'] == 'Test Dish'


def test_checkout_creates_order_with_server_pricing(auth, restaurant):
    item = restaurant.menu_items.first()
    response = auth.post(
        '/api/v1/orders/checkout/',
        {
            'restaurant_id': restaurant.pk,
            'items': [{'item_id': item.pk, 'quantity': 2}],
            'delivery': {'name': 'Test', 'phone': '9999999999', 'address': '1 Test Lane'},
        },
        format='json',
    )
    assert response.status_code == 201

    order = Order.objects.get(pk=response.data['order_id'])
    # 2 x 100 = 200 → free delivery (>=149); taxes = 5% + 6
    assert order.items_total == 200
    assert order.delivery_fee == 0
    assert str(order.grand_total) == '216.00'
    assert response.data['demo_mode'] is True  # no Razorpay keys in tests


def test_demo_payment_verification_marks_order_placed(auth, restaurant):
    item = restaurant.menu_items.first()
    checkout = auth.post(
        '/api/v1/orders/checkout/',
        {
            'restaurant_id': restaurant.pk,
            'items': [{'item_id': item.pk, 'quantity': 1}],
            'delivery': {'name': 'Test', 'phone': '9999999999', 'address': '1 Test Lane'},
        },
        format='json',
    ).data

    response = auth.post(
        '/api/v1/orders/verify-payment/', {'order_id': checkout['order_id']}, format='json'
    )
    assert response.status_code == 200
    assert response.data['status'] == Order.STATUS_PLACED
    assert Payment.objects.get(order__pk=checkout['order_id']).demo is True


def test_checkout_rejects_items_from_other_restaurant(auth, restaurant):
    other = Restaurant.objects.create(name='Other', cuisine='Other', rating='4.0')
    from restaurants.models import MenuCategory

    category = MenuCategory.objects.create(restaurant=other, name='Main')
    foreign_item = MenuItem.objects.create(
        restaurant=other, category=category, name='Foreign', price=50
    )

    response = auth.post(
        '/api/v1/orders/checkout/',
        {
            'restaurant_id': restaurant.pk,
            'items': [{'item_id': foreign_item.pk, 'quantity': 1}],
            'delivery': {'name': 'T', 'phone': '9999999999', 'address': 'X'},
        },
        format='json',
    )
    assert response.status_code == 400


def test_orders_are_private(auth, user, restaurant):
    other_user = User.objects.create_user(email='other@example.com', password='secret123')
    order = Order.objects.create(
        user=other_user,
        restaurant=restaurant,
        status=Order.STATUS_PLACED,
        items_total=100,
        delivery_fee=29,
        taxes=11,
        grand_total=140,
        delivery_name='O',
        delivery_phone='9',
        delivery_address='O',
    )
    assert auth.get(f'/api/v1/orders/{order.pk}/').status_code == 404
