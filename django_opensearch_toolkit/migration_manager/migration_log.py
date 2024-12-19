"""Document model for tracking the state of migrations.

We track migrations against a cluster using a dedicated index in the cluster.
Each document represents a single migration that was run/is running/failed to run.
This is similar to how Django uses a table in a RDBMS system to track its migrations
against that system, with each row being a seprate migration.
"""

import enum

from opensearchpy.helpers.document import Document
from opensearchpy.helpers.field import Date, Keyword, Integer, Text


class MigrationLogStatus(enum.Enum):
    """Valid values for the `status` field of MigrationLog."""

    IN_PROGRESS = "IN_PROGRESS"  # transient
    SUCCEEDED = "SUCCEEDED"  # terminal
    FAILED = "FAILED"  # terminal


class MigrationLog(Document):
    """A log of a single migration that is run against an OpenSearch cluster."""

    # Global ordering for the application of migrations
    order = Integer()

    # User-Supplied Data
    key = Keyword()  # unique identifier among all migrations for a cluster
    operation = Text(analyzer="keyword")  # the operation that was performed

    # Tracking data
    started_at = Date()
    ended_at = Date()
    status = Keyword()

    class Index:
        """Configuration for the index."""

        name = ".opensearch_toolkit.migration_log"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "hidden": True,
        }

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the document."""
        super().__init__(*args, **kwargs)
        self.__dict__["meta"]["id"] = self.key  # set the document_id for unique lookup
