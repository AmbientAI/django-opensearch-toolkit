"""A single merchant in the product catalog."""

import pprint

from opensearchpy.helpers.document import Document
from opensearchpy.helpers.field import Date, Keyword, Text


class Merchant(Document):
    """A single merchant in the product catalog."""

    name = Keyword()
    description = Text(analyzer="none")
    website = Keyword()

    created = Date()
    updated = Date()
    deleted = Date()

    class Index:
        using = "sample_app"  # cluster/connection name
        name = "merchants"  # index name


if __name__ == "__main__":
    pprint.pprint(Merchant()._index.to_dict())
