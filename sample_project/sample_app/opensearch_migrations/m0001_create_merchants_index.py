"""Sample migration #1."""

import json
from logging import getLogger

from opensearchpy.connection import connections
from opensearchpy.exceptions import NotFoundError

from django_opensearch_toolkit.migration_manager import OpenSearchMigration


_logger = getLogger(__name__)


class CreateMerchantsIndex(OpenSearchMigration):
    """Create the `merchants` index."""

    _KEY = "0001_create_merchants_index"
    _DESCRIPTION = "Create the merchants index"

    _CONNECTION_NAME = "sample_app"
    _INDEX_NAME = "merchants"
    _CREATE_INDEX_REQUEST_BODY = {
        "settings": {
            "index": {
                "number_of_shards": "2",
                "number_of_replicas": "1",
            },
        },
        "mappings": {
            "dynamic": "strict",  # prevent unrecognized fields
            "dynamic_templates": [],
            "properties": {
                # NOTE: these are generated from Merchant._index.to_dict()
                # and copy-pasted here, so that the migration is immutable.
                "created": {"type": "date"},
                "deleted": {"type": "date"},
                "description": {"analyzer": "english", "type": "text"},
                "name": {"type": "keyword"},
                "updated": {"type": "date"},
                "website": {"type": "keyword"},
            },
        },
        "aliases": {},
    }

    def __init__(self) -> None:
        """Initialize the migration."""
        super().__init__(key=self._KEY)

    def serialize(self) -> str:
        """Return a textual description of the migration run to store in the log."""
        return self._DESCRIPTION

    def apply(self, connection_name: str) -> bool:
        """Perform the migration."""
        assert connection_name == self._CONNECTION_NAME
        client = connections.get_connection(connection_name)

        try:
            client.indices.get(index=self._INDEX_NAME)
            _logger.error(f"Found existing index with name: {self._INDEX_NAME}")
            return False
        except NotFoundError:
            pass

        response = client.indices.create(
            index=self._INDEX_NAME,
            body=json.dumps(self._CREATE_INDEX_REQUEST_BODY),
        )
        _logger.info(f"{response}")
        return True
