from django.urls import path

from .views import (CategoryProductListView, ContactView, ProductCreateView, ProductDeleteView, ProductDetailView,
                    ProductListView, ProductUpdateView)

app_name = "catalog"

urlpatterns = [
    path("", ProductListView.as_view(), name="home"),
    path("contacts/", ContactView.as_view(), name="contact"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("product/create/", ProductCreateView.as_view(), name="product_create"),
    path("product/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("product/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("category/<int:pk>/", CategoryProductListView.as_view(), name="category_products"),
]
