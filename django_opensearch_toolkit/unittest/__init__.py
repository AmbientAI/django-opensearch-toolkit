"""Tools to implement unit tests requiring a mock OpenSearch client.

TODO(dtag): Create a test runnner that runs against a real, local OpenSearch cluster,
the same way Django runs tests against a local DB, but using a separate db namespace.
"""

from .base_tests import (
    FakeOpenSearchTestCase,
    MagicMockOpenSearchTestCase,
)
