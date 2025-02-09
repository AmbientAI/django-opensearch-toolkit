"""App configuration for django-opensearch-toolkit."""

from typing import Any, Dict

from django.apps import AppConfig
from django.conf import settings
from opensearchpy.connection import connections


_OpenSearchClusterName = str
_OpenSearchConfiguration = Dict[str, Any]


class DjangoOpensearchToolkitConfig(AppConfig):
    """App configuration for django-opensearch-toolkit."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_opensearch_toolkit"
    verbose_name = "Django OpenSearch Toolkit"

    def ready(self) -> None:
        """Initialize the app."""
        cluster_configurations = _get_opensearch_cluster_configurations()
        connections.configure(**cluster_configurations)


def _get_opensearch_cluster_configurations() -> Dict[_OpenSearchClusterName, _OpenSearchConfiguration]:
    """Load the OpenSearch cluster configurations from the project settings file."""
    cluster_configurations = getattr(settings, "OPENSEARCH_CLUSTERS", {})

    if not isinstance(cluster_configurations, dict):
        raise ValueError("OPENSEARCH_CLUSTERS must be a dictionary. Please check your settings.py file.")

    for c_name, c_config in cluster_configurations.items():
        if not isinstance(c_name, str):
            raise ValueError(
                "All keys in OPENSEARCH_CLUSTERS must be strings. Please check your settings.py file."
            )
        if not isinstance(c_config, dict):
            raise ValueError(
                "All values in OPENSEARCH_CLUSTERS must be dictionaries. Please check your settings.py file."
            )

    return cluster_configurations
