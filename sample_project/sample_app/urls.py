"""URL configuration for sample_app app."""

from django.urls import path

from sample_app.views.merchants_view import MerchantView


urlpatterns = [
    path("merchants/", MerchantView.as_view(), name="merchants-list"),
]
