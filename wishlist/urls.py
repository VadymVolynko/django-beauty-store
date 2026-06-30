from django.urls import path

from wishlist import views

urlpatterns = [
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views.wishlist_add, name="wishlist-add"),
    path("wishlist/remove/<int:product_id>/", views.wishlist_remove, name="wishlist-remove"),
]
