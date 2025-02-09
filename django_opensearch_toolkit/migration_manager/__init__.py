"""A tool to manage OpenSearch migrations.

A migration in this context is anything that changes the state of an OpenSearch
cluster outside the data itself. This could be cluster settings, creation of
specific indices or lifecycle policies on them, changes to mappings, etc.

These are analagous to Django migrations and this package aims to provide a
lightweight version of what Django migrations provides for RDBMS databases.
"""

from .opensearch_migration import OpenSearchMigration
