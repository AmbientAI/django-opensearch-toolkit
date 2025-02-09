"""Document model for tracking the state of migrations.

We track migrations against a cluster using a dedicated index in the cluster.
Each document represents a single migration that was run/is running/failed to run.
This is similar to how Django uses a table in a RDBMS databases to track its
migrations against that database, with each row being a separate migration.
"""

import enum

from opensearchpy.helpers.document import Document
from opensearchpy.helpers.field import Date, Keyword, Integer, Text


@enum.unique
class MigrationLogStatus(enum.Enum):
    """Valid values for the `status` field of MigrationLog."""

    IN_PROGRESS = "IN_PROGRESS"  # migration is currently being applied (transient)
    SUCCEEDED = "SUCCEEDED"  # migration has completed successfully (terminal)
    FAILED = "FAILED"  # migration failed during application (terminal)


class MigrationLog(Document):
    """A log of a single migration that is run against an OpenSearch cluster."""

    # Global ordering for the application of migrations
    order = Integer(required=True)

    # User-Supplied Data
    key = Keyword(required=True)  # unique identifier among all migrations for a cluster
    operation = Text(analyzer="keyword", required=True)  # the operation that was performed

    # Tracking data
    status = Keyword(required=True)
    started_at = Date(required=True)
    ended_at = Date()  # Optional as it's not set until completion

    class Index:
        """Configuration for the index."""

        name = ".django_opensearch_toolkit.migration_log"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "hidden": True,
        }

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the document.

        Sets the document ID to match the migration key for unique lookup capability.
        """
        super().__init__(*args, **kwargs)
        self.__dict__["meta"]["id"] = self.key
