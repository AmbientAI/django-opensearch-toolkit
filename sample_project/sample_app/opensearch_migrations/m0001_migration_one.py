"""Sample migration #1."""

from opensearchpy.connection import connections

from django_opensearch_toolkit.migration_manager import OpenSearchMigration


class SampleMigration0001(OpenSearchMigration):
    """Sample migration #1."""

    _KEY = "0001_migration_one"
    _DESCRIPTION = "Sample migration #1"

    def __init__(self) -> None:
        """Initialize the migration."""
        super().__init__(key=self._KEY)

    def serialize(self) -> str:
        """Return a textual description of the migration run to store in the log."""
        return self._DESCRIPTION

    def apply(self, connection_name: str) -> bool:
        """Perform the migration."""
        client = connections.get_connection(connection_name)
        del client  # Use the low-level client to execute commands against the cluster
        return True  # return True on success, False on failure
