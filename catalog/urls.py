from django.urls import path
from catalog.views import (
    ProductCreateView,
    ProductDeleteView,
    ProductManageListView,
    ProductUpdateView,
    brand_products_view,
    catalog_view,
    home_view,
    product_view,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("catalog/", catalog_view, name="catalog"),
    path("catalog/brand/<slug:slug>/", brand_products_view, name="catalog-brand"),
    path("owner/products/", ProductManageListView.as_view(), name="owner-products"),
    path("owner/products/add/", ProductCreateView.as_view(), name="owner-product-add"),
    path("owner/products/<slug:slug>/edit/", ProductUpdateView.as_view(), name="owner-product-edit"),
    path("owner/products/<slug:slug>/delete/", ProductDeleteView.as_view(), name="owner-product-delete"),
    path("catalog/<slug:slug>/", product_view, name="product"),
]
