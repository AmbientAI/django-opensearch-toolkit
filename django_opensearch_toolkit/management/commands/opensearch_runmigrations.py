"""Custom django-admin (manage.py) command for running migrations for an OpenSearch cluster."""

from typing import Any

from django.core.management.base import CommandError, CommandParser

from django_opensearch_toolkit.management.commands._opensearch_command import OpenSearchCommand
from django_opensearch_toolkit.migration_manager.migration_manager import OpenSearchMigrationsManager


class Command(OpenSearchCommand):
    """Custom django-admin (manage.py) command for running migrations for an OpenSearch cluster."""

    help = "Run migrations for an OpenSearch cluster"

    def add_arguments(self, parser: CommandParser) -> None:
        """Define arguments for this command."""
        parser.add_argument(
            "cluster",
            type=str,
            choices=self.available_clusters,
            help="Cluster Name",
        )
        parser.add_argument(
            "--nodry",
            dest="dry",
            action="store_false",
            default=True,
            help="Run in non-dry mode, i.e. apply the migrations. Default is dry.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Run the command."""
        del args  # unused
        cluster: str = options["cluster"]
        dry: bool = options["dry"]

        migrations = self.migrations_by_cluster.get(cluster, [])
        if len(migrations) == 0:
            raise CommandError(f"No migrations available for cluster={cluster}")

        manager = OpenSearchMigrationsManager(connection_name=cluster)
        manager.run_migrations(migrations=migrations, dry=dry)
