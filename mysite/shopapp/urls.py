from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter
from .views import (
    OrdersListView,
    OrderCreateView,
    ShopIndexView,
    GroupsListView,
    ProductDetailsView,
    ProductsListView,
    OrdersDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrderUpdateView,
    OrderDeleteView,
    ProductsExportView,
    OrdersExportView,
    ProductViewSet,
    OrderViewSet,
    LatestProductsFeed,
    UserOrdersListView,
    UserOrdersExportView,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("ordrers", OrderViewSet)

urlpatterns = [
    # path("", cache_page(180)(ShopIndexView.as_view()), name="index"),
    path("", ShopIndexView.as_view(), name="index"),

    path("api/", include(routers.urls)),
    path("users/<int:pk>/orders/", UserOrdersListView.as_view(), name="users_orders"),
    path("users/<int:pk>/orders/export/", UserOrdersExportView.as_view(), name="users_orders_export"),

    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/export/", ProductsExportView.as_view(), name="products_export"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive", ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", OrdersListView.as_view(), name="order_list"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/export/", OrdersExportView.as_view(), name="order_export"),
    path("orders/<int:pk>/", OrdersDetailView.as_view(), name="order_details"),
    path("orders/<int:pk>/update", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete", OrderDeleteView.as_view(), name="order_delete"),
    path("products/latest/feed", LatestProductsFeed(), name="products-feed"),
]
