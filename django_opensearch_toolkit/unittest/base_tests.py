"""Base classes for unittests requiring an OpenSearch client."""

import abc
from typing import Any, List, Set
from unittest.mock import MagicMock

from django.test import TestCase
from openmock import FakeOpenSearch
from opensearchpy.connection import connections


class _OpenSearchTestCase(TestCase, abc.ABC):
    """Base class for OpenSearch test cases."""

    # By default, assume Django-managed DBs are not needed to speed up the test
    # runner. Derived classes should override this if that is not the case.
    databases: Set[str] = set()

    # A mocked connection with this alias is always available for tests.
    unittest_connection: str = "unittest"

    def connections_to_patch(self) -> List[str]:
        """Return a list of OpenSearch connection aliases to patch."""
        return []

    @abc.abstractmethod
    def create_test_client(self) -> Any:
        """Create a mock OpenSearch client.

        Implement this method in derived classes to return a mock OpenSearch low-level client.
        """
        ...

    def setUp(self) -> None:
        """Set up the test case."""
        super().setUp()

        self._original_connections = {}

        for conn_alias in self.connections_to_patch():
            self._original_connections[conn_alias] = connections.get_connection(alias=conn_alias)
            connections.add_connection(conn_alias, self.create_test_client())

        connections.add_connection(self.unittest_connection, self.create_test_client())

    def tearDown(self) -> None:
        """Tear down the test case."""
        connections.remove_connection(self.unittest_connection)

        for conn_alias in self.connections_to_patch():
            connections.add_connection(conn_alias, self._original_connections[conn_alias])

        super().tearDown()

    def get_test_client(self, connection_name: str) -> MagicMock:
        """Get the mock OpenSearch client for the given connection name."""
        return connections.get_connection(alias=connection_name)


class MagicMockOpenSearchTestCase(_OpenSearchTestCase):
    """Base class for OpenSearch test cases using Python's built-in MagicMock as the mock client.

    Derived classes should implement return_value and side_effect behavior
    on the mock's methods, and inspect the call values.
    """

    def create_test_client(self) -> MagicMock:
        """Create a mock OpenSearch client."""
        return MagicMock()


class FakeOpenSearchTestCase(_OpenSearchTestCase):
    """Base class for OpenSearch test cases using openmock.FakeOpenSearch as the mock client.

    WARNING: this mock client does not implement all the behavior of a real
    OpenSearch client. E.g., search() just returns all docs in the index.
    """

    def create_test_client(self) -> FakeOpenSearch:
        """Create a mock OpenSearch client."""
        return FakeOpenSearch()
