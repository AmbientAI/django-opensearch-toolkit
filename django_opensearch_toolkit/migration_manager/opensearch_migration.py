"""Convention for specifying a migration to run against an OpenSearch cluster."""

import abc
from typing import Final


class OpenSearchMigration(abc.ABC):
    """Base class for user-specified OpenSearch migrations.

    Migrations are specified by implementing a derived class and implementing
    the abstract methods. Stateful operations against the cluster should be
    performed in the apply() method using the supplied connection_name.
    """

    def __init__(self, key: str) -> None:
        """Initialize the migration with a unique identifier.

        Args:
            key: A globally unique identifier for this migration.
        """
        if not key.strip():
            raise ValueError("Migration key cannot be empty")
        self._key: Final[str] = key

    def get_key(self) -> str:
        """Return a globally unique key among all migrations for a given cluster."""
        return self._key

    @abc.abstractmethod
    def serialize(self) -> str:
        """Return a textual description of the migration run to store in the log."""
        pass

    @abc.abstractmethod
    def apply(self, connection_name: str) -> bool:
        """Perform the migration against the specified connection.

        Args:
            connection_name: The name of the OpenSearch connection to use.

        Returns:
            bool: True if the migration was successful, False otherwise.
        """
        pass
