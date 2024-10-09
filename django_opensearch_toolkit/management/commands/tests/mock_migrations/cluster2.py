from typing import List

from django_opensearch_toolkit.migration_manager import OpenSearchMigration


class Migration1(OpenSearchMigration):
    """Fake migration for unittests."""

    def __init__(self) -> None:
        super().__init__("Migration1")

    def serialize(self) -> str:
        """Return a textual description of the migration run to store in the log."""
        return self._key

    def apply(self, connection_name: str) -> bool:
        """Perform the migration."""
        return True


class Migration2(OpenSearchMigration):
    """Fake migration for unittests."""

    def __init__(self) -> None:
        super().__init__("Migration2")

    def serialize(self) -> str:
        """Return a textual description of the migration run to store in the log."""
        return self._key

    def apply(self, connection_name: str) -> bool:
        """Perform the migration."""
        return True


MIGRATIONS: List[OpenSearchMigration] = [
    Migration1(),
    Migration2(),
]
