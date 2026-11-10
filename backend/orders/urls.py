from django.urls import path

from . import views

urlpatterns = [
    path('orders/checkout/', views.CheckoutView.as_view(), name='order-checkout'),
    path('orders/verify-payment/', views.VerifyPaymentView.as_view(), name='order-verify-payment'),
    path('orders/', views.MyOrdersView.as_view(), name='my-orders'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/advance/', views.AdvanceOrderView.as_view(), name='order-advance'),
    path('orders/<int:pk>/cancel/', views.CancelOrderView.as_view(), name='order-cancel'),
    path('payments/webhook/', views.RazorpayWebhookView.as_view(), name='razorpay-webhook'),
]
