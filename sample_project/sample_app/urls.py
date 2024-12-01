"""URL configuration for sample_app."""

from django.urls import path

from .views.merchants_view import MerchantView


urlpatterns = [
    path("merchants/", MerchantView.as_view(), name="merchants-list"),
]
