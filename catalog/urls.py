from django.urls import path
from catalog.views import home_view, catalog_view, product_view

urlpatterns = [
    path("", home_view, name="home"),
    path("catalog/", catalog_view, name="catalog"),
    path("catalog/<slug:slug>/", product_view, name="product"),
]
