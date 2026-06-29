from django.urls import path
from cart.views import cart_add, cart_remove, cart_update, cart_view

urlpatterns = [
    path("cart/", cart_view, name="cart"),
    path("cart/add/<int:product_id>/", cart_add, name="cart-add"),
    path("cart/remove/<int:product_id>/", cart_remove, name="cart-remove"),
    path("cart/update/<int:product_id>/", cart_update, name="cart-update"),
]
