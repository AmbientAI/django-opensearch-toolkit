"""A single item in the product catalog."""

import pprint

from opensearchpy.helpers.document import Document
from opensearchpy.helpers.field import Date, Keyword, Long, Text


class Product(Document):
    """A single item in the product catalog."""

    name = Text(analyzer="english")
    description = Text(analyzer="english")
    price = Long()  # price in cents
    merchant_id = Keyword()

    created = Date()
    updated = Date()
    deleted = Date()

    class Index:
        using = "sample_app"  # cluster/connection name
        name = "products"  # index name


if __name__ == "__main__":
    pprint.pprint(Product()._index.to_dict())
