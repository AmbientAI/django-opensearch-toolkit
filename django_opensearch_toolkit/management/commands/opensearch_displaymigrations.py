"""Custom django-admin (manage.py) command for displaying migrations for an OpenSearch cluster."""

from typing import Any

from django.core.management.base import CommandParser

from django_opensearch_toolkit.management.commands._opensearch_command import OpenSearchCommand
from django_opensearch_toolkit.migration_manager.migration_manager import OpenSearchMigrationsManager


class Command(OpenSearchCommand):
    """Custom django-admin (manage.py) command for displaying migrations for an OpenSearch cluster."""

    help = "Display previously-run migrations for an OpenSearch cluster"

    def add_arguments(self, parser: CommandParser) -> None:
        """Define arguments for this command."""
        parser.add_argument(
            "cluster",
            type=str,
            choices=self.available_clusters,
            help="Cluster Name",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Run the command."""
        del args  # unused
        cluster: str = options["cluster"]

        manager = OpenSearchMigrationsManager(connection_name=cluster)
        manager.display_migrations()
