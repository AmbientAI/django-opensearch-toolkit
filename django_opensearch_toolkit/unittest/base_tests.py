"""Base classes for unittests requiring a mock OpenSearch client."""

from typing import Set
from unittest.mock import patch, MagicMock

from django.test import TestCase
from openmock import FakeOpenSearch
from opensearchpy.connection import connections


class MagicMockOpenSearchBaseTest(TestCase):
    """Base class using Python's built-in MagicMock as the mock client.

    Derived classes should implement return_value and side_effect behavior
    on the mock's methods, and inspect the call values.

    Derived classes can access the mock OpenSearch client either:
      - Directly via self.test_client
      - Indirectly by using opensearch-dsl and self.connection_name. This
        will resolve to the same low-level OpenSearch client.
    """

    # By default, assume Django-managed DBs are not needed to speed up the test
    # runner. Derived classes should override this if that is not the case.
    databases: Set[str] = set()
    test_client: MagicMock

    def setUp(self) -> None:
        """Set up the test case."""
        super().setUp()

        self.connection_name = "unittest-connection"

        # The opensearchpy.connections module imports the OpenSearch client
        # by name, so we need to patch it this way
        with patch("opensearchpy.OpenSearch", MagicMock):
            connections.create_connection(alias=self.connection_name, hosts=["fake-host"])

        self.test_client = connections.get_connection(alias=self.connection_name)


class FakeOpenSearchBaseTest(TestCase):
    """Base class using openmock.FakeOpenSearch as the mock client.

    WARNING: this mock client does not implement all the behavior of a real
    ES client. E.g., search() just returns all docs in the index.

    Derived classes can access the mock ES client either:
      - Directly via self.test_client
      - Indirectly by using opensearch-dsl and self.connection_name. This
        will resolve to the same low-level OpenSearch client.
    """

    # By default, assume Django-managed DBs are not needed to speed up the test
    # runner. Derived classes should override this if that is not the case.
    databases: Set[str] = set()
    test_client: FakeOpenSearch

    def setUp(self) -> None:
        """Set up the test case."""
        super().setUp()

        self.connection_name = "unittest-connection"

        # The opensearchpy.connections module imports the OpenSearch
        # by name, so we need to patch it this way
        with patch("opensearchpy.OpenSearch", FakeOpenSearch):
            connections.create_connection(alias=self.connection_name, hosts=["fake-host"])

        self.test_client = connections.get_connection(alias=self.connection_name)
