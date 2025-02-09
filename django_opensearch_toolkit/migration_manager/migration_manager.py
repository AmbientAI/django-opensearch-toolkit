"""Utility class for managing the state of migrations against an OpenSearch cluster."""

from logging import getLogger
import time
from typing import Final, List, Sequence

from opensearchpy.client import OpenSearch
from opensearchpy.connection import connections
from opensearchpy.exceptions import ConflictError, NotFoundError
from opensearchpy.helpers.index import Index

from django_opensearch_toolkit.migration_manager.migration_log import MigrationLog, MigrationLogStatus
from django_opensearch_toolkit.migration_manager.opensearch_migration import OpenSearchMigration


_logger = getLogger(__name__)


class OpenSearchMigrationsManager:
    """Utility class for managing the state of migrations against an OpenSearch cluster."""

    def __init__(self, connection_name: str, max_migrations_to_fetch: int = 5_000) -> None:
        """Initialize the manager.

        NOTE: this implementation will fetch all migration logs in one shot and
        load them into memory. This should be perfectly fine for a long time. If
        the number of migration logs grows very large, we could batch load these.
        The implementation here is correct only if the number of logs is less than
        the `max_migrations_to_fetch` parameter.
        """
        self.connection_name: Final[str] = connection_name
        self.max_migrations_to_fetch: Final[int] = max_migrations_to_fetch
        self.migration_log_index: Final[Index] = Index(
            name=MigrationLog.Index.name,
            using=self.connection_name,
        )
        self.client: Final[OpenSearch] = connections.get_connection(self.connection_name)  # low-level client

    # Public Methods

    def display_migrations(self) -> None:
        """Display the migration log history."""
        self._create_migration_logs_index_if_not_exists()
        self._get_and_display_all_migration_logs()

    def run_migrations(self, migrations: Sequence[OpenSearchMigration], dry: bool = True) -> None:
        """Apply all migrations, skipping those that were already applied.

        Will abort on any faillure or any inconsistency in the migration log.
        """
        self._create_migration_logs_index_if_not_exists()
        self._log(f"Running {len(migrations)} migrations in mode {dry=}")

        # Retrieve the existing migrations
        existing_migration_logs = self._get_and_display_all_migration_logs()

        # Abort if any have failed or are in-progress
        any_failed_or_in_progress = any(
            log.status != MigrationLogStatus.SUCCEEDED.value for log in existing_migration_logs
        )
        if any_failed_or_in_progress:
            self._log(
                "Aborting because a failed or in-progress migration was found. "
                "Cluster may be in an inconsistent or transient state. "
                "Please fix before attempting to run this script again."
            )
            return

        # Apply migrations one-by-one
        for i, m in enumerate(migrations):
            # Check if the migration was already applied
            if len(existing_migration_logs) > i:
                if existing_migration_logs[i].order != i:
                    self._log("Aborting because migration history order is incorrect")
                    return

                if existing_migration_logs[i].key != m.get_key():
                    self._log(
                        f"Aborting because migration history doesn't match supplied migrations: "
                        f"Existing Migration at Position {i} = [{existing_migration_logs[i].key}] != "
                        f"Supplied Migration at Position {i} [{m.get_key()}]"
                    )
                    return

                else:
                    self._log(f"[key={m.get_key()}] Migration already applied. Skipping.")
                    continue

            # Migration not applied. Apply it now
            else:
                if dry:
                    self._log(f"[key={m.get_key()}] Skipping because in dry mode")

                else:
                    success = self._run_migration(order=i, migration=m)
                    if not success:
                        self._log("Aborting because a migration failed to complete")
                        return

    # Private Methods

    def _log(self, message: str) -> None:
        """Log message with a custom prefix."""
        _logger.info(f"[{self.__class__.__name__}] {message}")

    def _create_migration_logs_index_if_not_exists(self) -> None:
        """Create the index that tracks the migration logs."""
        if not self.migration_log_index.exists():
            self._log("Creating migration logs index")
            MigrationLog.init(using=self.connection_name)

    def _delete_migration_logs_index_if_exists(self) -> None:
        """Delete the index that tracks the migration logs."""
        if self.migration_log_index.exists():
            self._log("Deleting migration logs index")
            self.migration_log_index.delete()

    def _print_migration_logs(self, migration_logs: List[MigrationLog]) -> None:
        """Pretty-print the provided migration logs."""
        for log in migration_logs:
            self._log(
                f"[order={log.order}, key={log.key}] status={log.status} : "
                f"(started_at={log.started_at}, ended_at={log.ended_at})"
            )

    def _get_all_migration_logs(self) -> List[MigrationLog]:
        """Fetch all migration logs in their applied order."""
        search = MigrationLog.search(using=self.connection_name)
        search = search.extra(size=self.max_migrations_to_fetch)
        search = search.sort("order")
        existing_migration_logs = list(search.execute().hits)
        return existing_migration_logs

    def _get_and_display_all_migration_logs(self) -> List[MigrationLog]:
        """Fetch all migration logs in their applied order, and print them."""
        existing_migration_logs = self._get_all_migration_logs()
        self._log(f"Found {len(existing_migration_logs)} existing migrations")
        self._print_migration_logs(existing_migration_logs)
        return existing_migration_logs

    def _create_migration_log_atomic(self, log: MigrationLog) -> bool:
        """Try to create the log as a document in the migration_log_index, and fail if it exists.

        We have this helper because MigrationLog.save() uses the `index` API instead
        of the `create` API. The Document helper does not expose access to the latter
        API, so we use the low-level client here.
        """
        # Try to create it
        try:
            response = self.client.create(
                index=MigrationLog.Index.name,
                id=log.meta.id,
                body=log.to_dict(include_meta=False),
            )
        except ConflictError:
            _logger.exception(
                "Migraton log already exists. There might be a concurrent script running these migrations."
            )
            return False

        # Confirm it succeeded
        if response["result"] != "created":
            self._log("Failed to create initial migration log")
            return False

        # Flush the index to ensure the document is persisted and check a search will find it
        self.migration_log_index.flush()
        try:
            log2 = MigrationLog.get(id=log.meta.id, using=self.connection_name)
        except NotFoundError:
            _logger.exception("Failed to find the migration log in the index")
            return False

        # Confirm the commited log is marked IN_PROGRESS
        if log2["status"] != MigrationLogStatus.IN_PROGRESS.value:
            self._log(f"Invalid status found for initial log: {log2['status']}")
            return False

        return True

    def _run_migration(self, order: int, migration: OpenSearchMigration) -> bool:
        """Apply a migration using write-ahead logging and terminal log updates."""
        started_at = int(1000 * time.time())

        def _print_progress(message: str) -> None:
            self._log(f"[key={migration.get_key()}] {message}")

        _print_progress("[1/4] Creating migration log")
        log = MigrationLog(
            order=order,
            key=migration.get_key(),
            operation=migration.serialize(),
            status=MigrationLogStatus.IN_PROGRESS.value,
            started_at=started_at,
            ended_at=None,
        )
        was_created = self._create_migration_log_atomic(log)
        if not was_created:
            self._log("Failed to create migration log")
            return False

        _print_progress("[2/4] Applying migration operation")
        success = False
        try:
            success = migration.apply(self.connection_name)
        except Exception:
            _logger.exception("Failed to apply migration")
        ended_at = int(1000 * time.time())
        new_status = MigrationLogStatus.SUCCEEDED.value if success else MigrationLogStatus.FAILED.value

        _print_progress(f"[3/4] Migration {new_status.lower()}; updating migration log")
        result = log.update(
            using=self.connection_name,
            # updated fields:
            status=new_status,
            ended_at=ended_at,
        )
        if result != "updated":
            self._log("Failed to update migration log")
            return False
        self.migration_log_index.flush()

        _print_progress("[4/4] Done")
        return success
