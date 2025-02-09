"""Common logic for all custom django-admin (manage.py) commands for the django_opensearch_toolkit."""

import importlib
from typing import Any, Dict, List

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_opensearch_toolkit.migration_manager import OpenSearchMigration


class OpenSearchCommand(BaseCommand):
    """Common logic for all custom django-admin (manage.py) commands for the django_opensearch_toolkit."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.available_clusters = self._get_clusters()
        assert len(self.available_clusters) > 0
        self.migrations_by_cluster = self._get_migrations_by_cluster(self.available_clusters)

    @staticmethod
    def _get_clusters() -> List[str]:
        clusters = getattr(settings, "OPENSEARCH_CLUSTERS", {})

        if not isinstance(clusters, dict):
            raise ValueError("OPENSEARCH_CLUSTERS must be a dictionary. Please check your settings.py file.")

        if len(clusters) == 0:
            raise CommandError(
                "No OpenSearch clusters available. "
                "Register clusters in settings.OPENSEARCH_CLUSTERS to use this command."
            )

        for cluster_name in clusters:
            if not isinstance(cluster_name, str):
                raise CommandError(
                    f"Invalid cluster name '{cluster_name}'. All cluster names must be strings."
                )

        available_clusters = list(clusters.keys())
        return available_clusters

    @staticmethod
    def _get_migrations_by_cluster(
        available_clusters: List[str],
    ) -> Dict[str, List[OpenSearchMigration]]:
        all_migration_paths = getattr(settings, "OPENSEARCH_MIGRATION_PATHS", {})

        if not isinstance(all_migration_paths, dict):
            raise CommandError("Invalid value for settings.OPENSEARCH_MIGRATION_PATHS. Must be a dictionary.")

        migrations_by_cluster: Dict[str, List[OpenSearchMigration]] = {}

        for cluster_name, migrations_path in all_migration_paths.items():
            if not isinstance(cluster_name, str):
                raise CommandError(
                    f"Invalid cluster name '{cluster_name}' for migration paths. "
                    "All cluster names must be strings."
                )
            if cluster_name not in available_clusters:
                raise CommandError(
                    f"Cluster '{cluster_name}' in settings.OPENSEARCH_MIGRATION_PATHS is not in "
                    "settings.OPENSEARCH_CLUSTERS."
                )
            try:
                migrations = importlib.import_module(migrations_path).MIGRATIONS
            except ModuleNotFoundError as e:
                raise CommandError(f"Module '{migrations_path}' not found") from e
            except AttributeError as e:
                raise CommandError(f"Module '{migrations_path}' must contain a 'MIGRATIONS' attribute") from e
            if not isinstance(migrations, list):
                raise CommandError(
                    f"Invalid value for migrations in '{migrations_path}.MIGRATIONS'. "
                    "Must be a list of migrations."
                )
            for migration in migrations:
                if not isinstance(migration, OpenSearchMigration):
                    raise CommandError(
                        f"Invalid migration in '{migrations_path}.MIGRATIONS'. "
                        "Must be an instance of OpenSearchMigration."
                    )
            migrations_by_cluster[cluster_name] = migrations

        return migrations_by_cluster
