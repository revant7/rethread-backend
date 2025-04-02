from . import views
from django.contrib import admin
from django.urls import path, re_path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
    TokenVerifyView,
)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema view configuration
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Welcome to the API documentation. Here, you can explore all available endpoints.",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("", views.index, name="index"),
    # customer-account-creation creation
    path(
        "create-customer-account/", views.create_customer_account, name="create_account"
    ),
    # account-verification
    path("token/", views.custom_token_obtain_view, name="token_obtain_pair"),
    path("verify-token/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # getting-new-products
    path("fetch-products/", views.fetch_products, name="products"),
    # rendering-products-endpoint
    path("get-products/", views.get_products, name="products"),
    path(
        "get-product-by-id/<str:unique_id>/", views.get_product_by_id, name="products"
    ),
    path("autocomplete/", views.autocomplete, name="autocomplete"),
    path("search-products/", views.search_products, name="products"),
    # get-profile-details
    path("get-profile-details/", views.get_profile_details, name="products"),
    # address-details
    path("get-address-details/", views.get_address_details, name="get-address-details"),
    path(
        "update-address-details/",
        views.update_address_details,
        name="update-address-details",
    ),
    path(
        "update-profile-details/",
        views.update_profile_details,
        name="update-profile-details",
    ),
    # orders-endpoints
    path("post-orders/", views.post_orders, name="post-orders"),
    path("get-orders/", views.get_orders, name="get-orders"),
    # cart-related-endpoints
    path("add-item-to-cart/", views.add_item_to_cart, name="add-item-to-cart"),
    path("get-cart-items/", views.get_cart_items, name="get-cart-items"),
    path(
        "get-cart-items-count/", views.get_cart_items_count, name="get-cart-items-count"
    ),
    path(
        "remove-item-from-cart/",
        views.remove_item_from_cart,
        name="remove-item-from-cart",
    ),
]
