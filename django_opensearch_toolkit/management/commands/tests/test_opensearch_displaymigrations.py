"""Unit tests for the `opensearch_displaymigrations` command."""

from typing import Any, Dict
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class TestDisplayMigrations(TestCase):
    """Unit tests for the `opensearch_displaymigrations` command."""

    databases = set()

    COMMAND_NAME = "opensearch_displaymigrations"

    def setUp(self) -> None:
        self.clusters: Dict[str, Dict[str, Any]] = {
            "cluster1": {},
            "cluster2": {},
            "cluster3": {},
        }
        self.migration_paths = {
            "cluster1": "django_opensearch_toolkit.management.commands.tests.mock_migrations.cluster1",
            "cluster2": "django_opensearch_toolkit.management.commands.tests.mock_migrations.cluster2",
            # missing path for cluster3, i.e., no available migrations
        }

    def _call_command(self, *args: Any, **kwargs: Any) -> None:
        with patch.object(settings, "OPENSEARCH_CLUSTERS", new=self.clusters, create=True):
            with patch.object(settings, "OPENSEARCH_MIGRATION_PATHS", new=self.migration_paths, create=True):
                call_command(self.COMMAND_NAME, *args, **kwargs)

    def test_cluster_required(self) -> None:
        """Test that an error is raised when a cluser is not provided."""
        with self.assertRaises(CommandError) as cm:
            self._call_command()
        self.assertEqual(
            str(cm.exception),
            "Error: the following arguments are required: cluster",
        )

    def test_cluster_invalid(self) -> None:
        """Test that an error is raised when an invalid cluster is provided."""
        with self.assertRaises(CommandError) as cm:
            self._call_command("invalid-cluster")
        self.assertRegex(
            str(cm.exception),
            r"Error: argument cluster: invalid choice: 'invalid-cluster' \(choose from '.*'\)",
        )
