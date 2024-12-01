"""Base classes for unittests requiring a mock OpenSearch client."""

from typing import List, Set
from unittest.mock import patch, MagicMock

from django.test import TestCase
from openmock import FakeOpenSearch
from opensearchpy.connection import connections


_PATCH_TARGET = "opensearchpy.OpenSearch"


class MagicMockOpenSearchTestCase(TestCase):
    """Base class using Python's built-in MagicMock as the mock client.

    Derived classes should implement return_value and side_effect behavior
    on the mock's methods, and inspect the call values.

    Derived classes can access the mock OpenSearch client either:
      - Directly via self.test_client
      - Indirectly by using opensearchpy.helpers and self.connection_name. This
        will resolve to the same low-level OpenSearch client.
    """

    # By default, assume Django-managed DBs are not needed to speed up the test
    # runner. Derived classes should override this if that is not the case.
    databases: Set[str] = set()

    def connections_to_patch(self) -> List[str]:
        return []

    def setUp(self) -> None:
        """Set up the test case."""
        super().setUp()

        self._original_connections = {}

        for conn_alias in self.connections_to_patch():
            self._original_connections[conn_alias] = connections.get_connection(alias=conn_alias)
            connections.add_connection(conn_alias, MagicMock())

    def tearDown(self) -> None:
        """Tear down the test case."""
        for conn_alias in self.connections_to_patch():
            connections.add_connection(conn_alias, self._original_connections[conn_alias])

        super().tearDown()

    def get_test_client(self, connection_name: str) -> MagicMock:
        """Get the mock OpenSearch client for the given connection name."""
        conn = connections.get_connection(alias=connection_name)
        assert isinstance(conn, MagicMock)
        return conn


class FakeOpenSearchTestCase(TestCase):
    """Base class using openmock.FakeOpenSearch as the mock client.

    WARNING: this mock client does not implement all the behavior of a real
    OpenSearch client. E.g., search() just returns all docs in the index.

    Derived classes can access the mock OpenSearch client either:
      - Directly via self.test_client
      - Indirectly by using opensearchpy.helpers and self.connection_name. This
        will resolve to the same low-level OpenSearch client.
    """

    # By default, assume Django-managed DBs are not needed to speed up the test
    # runner. Derived classes should override this if that is not the case.
    databases: Set[str] = set()

    connection_name: str
    test_client: FakeOpenSearch

    def setUp(self) -> None:
        """Set up the test case."""
        super().setUp()

        self.connection_name = "unittest-connection"

        with patch(_PATCH_TARGET, FakeOpenSearch):
            connections.create_connection(alias=self.connection_name, hosts=["fake-host"])

        self.test_client = connections.get_connection(alias=self.connection_name)

    def tearDown(self) -> None:
        """Tear down the test case."""
        super().tearDown()

        connections.remove_connection(self.connection_name)
