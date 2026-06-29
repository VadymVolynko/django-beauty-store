from django.urls import path
from orders.views import checkout_view, order_history_view, order_success_view

urlpatterns = [
    path("checkout/",            checkout_view,      name="checkout"),
    path("orders/success/<int:pk>/", order_success_view, name="order-success"),
    path("orders/",              order_history_view, name="order-history"),
]
