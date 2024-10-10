"""OpenSearch migrations for the sample_app."""

from typing import List

from django_opensearch_toolkit.migration_manager import OpenSearchMigration

from .m0001_migration_one import SampleMigration0001
from .m0002_migration_two import SampleMigration0002


# When making updates here, please note these guidelines:
#   - Don't remove an entry from this list
#   - Don't reorder entries
#   - Only add new entries at the end
# We use a serial migration order right now for OpenSearch. It's a dependency chain,
# instead of a more general dependency graph, like Django would create.
MIGRATIONS: List[OpenSearchMigration] = [
    SampleMigration0001(),
    SampleMigration0002(),
]
