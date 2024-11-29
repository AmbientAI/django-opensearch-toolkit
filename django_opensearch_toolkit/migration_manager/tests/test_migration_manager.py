"""Unit tests for OpenSearchMigrationsManager."""

from typing import Optional
from unittest.mock import MagicMock

from opensearchpy.exceptions import ConflictError
import parameterized as paramt

from django_opensearch_toolkit.migration_manager.migration_log import MigrationLog, MigrationLogStatus
from django_opensearch_toolkit.migration_manager.migration_manager import OpenSearchMigrationsManager
from django_opensearch_toolkit.migration_manager.opensearch_migration import OpenSearchMigration
from django_opensearch_toolkit.unittest import FakeOpenSearchTestCase, MagicMockOpenSearchTestCase


class SampleMigration(OpenSearchMigration):
    """Migraton for unit test."""

    _KEY = "0001_test_migration"
    _DESCRIPTION = "This is a test migration"

    def __init__(self, return_value: bool, should_raise: bool, key: str = _KEY):
        """Initialize the migration."""
        super().__init__(key=key)
        self.return_value = return_value
        self.should_raise = should_raise
        self.apply_was_run_with: Optional[str] = None

    def serialize(self) -> str:
        """Return a textual description of the migration run to store in the log."""
        return self._DESCRIPTION

    def apply(self, connection_name: str) -> bool:
        """Perform the migration."""
        self.apply_was_run_with = connection_name
        if self.should_raise:
            raise ValueError("Simulate failed migration")
        return self.return_value


class OpenSearchMigrationsManagerTest01(FakeOpenSearchTestCase):
    """Part 1 unit tests for OpenSearchMigrationsManager.

    These tests are simpler to write with the FakeOpenSearch mock client.
    """

    def setUp(self) -> None:
        super().setUp()
        self.manager = OpenSearchMigrationsManager(connection_name=self.connection_name)
        self.assertEqual(self.manager.client, self.test_client)

    def test_index_management(self) -> None:
        """Test the methods that create and delete the migration log index."""
        self.assertFalse(self.test_client.indices.exists(MigrationLog.Index.name))

        for _ in range(3):
            self.manager._create_migration_logs_index_if_not_exists()  # idempodent
            self.assertTrue(self.test_client.indices.exists(MigrationLog.Index.name))

        for _ in range(3):
            self.manager._delete_migration_logs_index_if_exists()  # idempodent
            self.assertFalse(self.test_client.indices.exists(MigrationLog.Index.name))

    def _create_migration_log(self, log: MigrationLog) -> None:
        self.test_client.index(
            index=MigrationLog.Index.name,
            id=log.meta.id,
            body=log.to_dict(include_meta=False),
        )

    def test_get_all_migration_logs(self):
        """Test _get_all_migration_logs() and _get_and_display_all_migration_logs()."""
        self.manager._create_migration_logs_index_if_not_exists()

        # Initially, no logs
        self.assertListEqual([], self.manager._get_all_migration_logs())
        self.assertListEqual([], self.manager._get_and_display_all_migration_logs())

        # Create some logs
        logs = [
            MigrationLog(order=2, key="id_0002"),
            MigrationLog(order=1, key="id_0001"),
            MigrationLog(order=3, key="id_0003"),
        ]
        for log in logs:
            self._create_migration_log(log)

        # Confirm they are returned
        # NOTE: they should be returned in order. Unfortunately, the FakeOpenSearch
        # client just returns everything in the index and doesn't respect the
        # query params, including sort()
        expected_keys = set(["id_0001", "id_0002", "id_0003"])
        self.assertSetEqual(
            expected_keys,
            set(log.key for log in self.manager._get_all_migration_logs()),
        )
        self.assertSetEqual(
            expected_keys,
            set(log.key for log in self.manager._get_and_display_all_migration_logs()),
        )

    def test_run_migrations_empty(self) -> None:
        """Test run_migrations() when supplied with no migrations."""
        # Initially no index
        self.assertFalse(self.test_client.indices.exists(MigrationLog.Index.name))

        # Run empty migrations
        self.manager.run_migrations([])

        # Index is created, but there's no docs in it
        self.assertTrue(self.test_client.indices.exists(MigrationLog.Index.name))

    @paramt.parameterized.expand(
        [
            (MigrationLogStatus.IN_PROGRESS.value,),
            (MigrationLogStatus.FAILED.value,),
        ]
    )
    def test_run_migrations_failed_or_inprogress(self, status: str) -> None:
        """Test run_migrations() when there's existing failed or in-progress migrations."""
        self.manager._create_migration_logs_index_if_not_exists()
        self._create_migration_log(
            MigrationLog(
                order=0,
                key="id_0001",
                status=status,
            )
        )
        self.assertEqual(len(self.manager._get_all_migration_logs()), 1)

        self.manager._run_migration = MagicMock()  # type: ignore[method-assign]
        self.manager.run_migrations([])

        # We abort before running any migrations
        self.manager._run_migration.assert_not_called()

    def test_run_migrations_history_mismatch(self) -> None:
        """Test run_migrations() when there's existing a mismatch in the migration history."""
        self.manager._create_migration_logs_index_if_not_exists()
        self._create_migration_log(
            MigrationLog(
                order=0,
                key="id_0001",
                status=MigrationLogStatus.SUCCEEDED.value,
            )
        )
        self.assertEqual(len(self.manager._get_all_migration_logs()), 1)

        self.manager._run_migration = MagicMock()  # type: ignore[method-assign]
        migrations = [
            SampleMigration(True, False),  # key doesn't match what's in the log
        ]
        self.manager.run_migrations(migrations)

        # We abort before running any migrations
        self.manager._run_migration.assert_not_called()

    @paramt.parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_run_migrations_succeeds(self, dry: bool) -> None:
        """Test a successful run of run_migrations()."""
        self.manager._create_migration_logs_index_if_not_exists()
        self._create_migration_log(
            MigrationLog(
                order=0,
                key="id_0001",
                status=MigrationLogStatus.SUCCEEDED.value,
            )
        )
        self._create_migration_log(
            MigrationLog(
                order=1,
                key="id_0002",
                status=MigrationLogStatus.SUCCEEDED.value,
            )
        )
        self.assertEqual(len(self.manager._get_all_migration_logs()), 2)

        self.manager._run_migration = MagicMock()  # type: ignore[method-assign]
        migrations = [
            # these were already applied
            SampleMigration(True, False, key="id_0001"),
            SampleMigration(True, False, key="id_0002"),
            # this needs to be applied
            SampleMigration(True, False, key="id_0003"),
        ]
        self.manager.run_migrations(migrations, dry=dry)

        if dry:
            self.manager._run_migration.assert_not_called()
        else:
            self.manager._run_migration.assert_called_once_with(order=2, migration=migrations[2])


class OpenSearchMigrationsManagerTest02(MagicMockOpenSearchTestCase):
    """Part 2 unit tests for OpenSearchMigrationsManager.

    These tests are simpler to write with the MagicMock mock client.
    """

    def setUp(self) -> None:
        super().setUp()
        self.manager = OpenSearchMigrationsManager(connection_name=self.connection_name)
        self.assertEqual(self.manager.client, self.test_client)
        self.test_client.reset_mock()

    def test_create_migration_log_atomic_success(self) -> None:
        """Test for _create_migration_log_atomic() that succeeds."""
        log = MigrationLog(order=13, key="id_0013")

        # Mock the resposes of the OpenSearch Client
        self.test_client.create.return_value = {"result": "created"}
        self.test_client.get.return_value = {
            "found": True,
            "_index": MigrationLog.Index.name,
            "_id": "id_0013",
            "_source": {
                "status": MigrationLogStatus.IN_PROGRESS.value,
            },
        }

        # Try to create the log
        success = self.manager._create_migration_log_atomic(log)
        self.assertTrue(success)

        # Confirm the calls that were issued against the OpenSearch client
        #  1. Create the document: should have correct index, id, and body
        #  2. Flush the correct index
        #  3. Get the correct document to ensure it exists
        self.assertEqual(len(self.test_client.mock_calls), 3)
        self.test_client.create.assert_called_once_with(
            index=MigrationLog.Index.name,
            id="id_0013",
            body=log.to_dict(include_meta=False),
        )
        self.test_client.indices.flush.assert_called_once_with(
            index=MigrationLog.Index.name,
        )
        self.test_client.get.assert_called_once_with(
            index=MigrationLog.Index.name,
            id="id_0013",
        )

    def test_create_migration_log_atomic_fails_duplicate(self) -> None:
        """Test for _create_migration_log_atomic() that fails b/c of a duplicate log."""
        log = MigrationLog(order=13, key="id_0013")

        # Mock the resposes of the OpenSearch Client
        self.test_client.create.side_effect = ConflictError("Duplicate object")

        # Try to create the log
        success = self.manager._create_migration_log_atomic(log)
        self.assertFalse(success)

        # Confirm the calls that were issued against the OpenSearch client
        #  1. Create the document: should have correct index, id, and body
        #  -- fails after this, so no more calls
        self.assertEqual(len(self.test_client.mock_calls), 1)
        self.test_client.create.assert_called_once_with(
            index=MigrationLog.Index.name,
            id="id_0013",
            body=log.to_dict(include_meta=False),
        )

    @paramt.parameterized.expand(
        [
            (True, False),
            (False, False),
            (True, True),
            (False, True),
        ]
    )
    def test_run_migration(self, return_value: bool, should_raise: bool) -> None:
        """Test the _run_migration() method."""
        order = 12
        migration = SampleMigration(return_value=return_value, should_raise=should_raise)

        # Mock the resposes of the OpenSearch Client
        self.test_client.create.return_value = {"result": "created"}
        self.test_client.get.return_value = {
            "found": True,
            "_index": MigrationLog.Index.name,
            "_id": migration.get_key(),
            "_source": {
                "status": MigrationLogStatus.IN_PROGRESS.value,
            },
        }
        self.test_client.update.return_value = {"result": "updated"}

        # Attempt to run the Migration
        success = self.manager._run_migration(order=order, migration=migration)
        should_succeed = return_value and not should_raise
        expected_final_status = (
            MigrationLogStatus.SUCCEEDED.value if should_succeed else MigrationLogStatus.FAILED.value
        )
        self.assertEqual(success, should_succeed)
        self.assertEqual(migration.apply_was_run_with, self.connection_name)

        # Check that the migration log was initially created
        create_kwargs = self.test_client.create.mock_calls[0].kwargs
        create_kwargs_start_at = create_kwargs["body"]["started_at"]
        self.assertDictEqual(
            create_kwargs,
            {
                "index": MigrationLog.Index.name,
                "id": migration.get_key(),
                "body": {
                    "order": order,
                    "key": migration.get_key(),
                    "operation": migration.serialize(),
                    "started_at": create_kwargs_start_at,
                    "status": MigrationLogStatus.IN_PROGRESS.value,  # created with IN_PROGRESS
                },
            },
        )

        # Check that the migration log was updated
        update_kwargs = self.test_client.update.mock_calls[0].kwargs
        update_kwargs_end_at = update_kwargs["body"]["doc"]["ended_at"]
        self.assertDictEqual(
            update_kwargs,
            {
                "index": MigrationLog.Index.name,
                "id": migration.get_key(),
                "body": {
                    "doc_as_upsert": False,
                    "detect_noop": True,
                    "doc": {
                        "ended_at": update_kwargs_end_at,
                        "status": expected_final_status,  # correct terminal status
                    },
                },
                "refresh": False,
                "retry_on_conflict": 0,
            },
        )

        self.assertLessEqual(create_kwargs_start_at, update_kwargs_end_at)
