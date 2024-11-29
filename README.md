# django-opensearch-toolkit

A Django app for interacting with OpenSearch clusters, including connection management, migrations, search, and unit tests.

It is implemented as a thin wrapper over the [opensearch-py](https://pypi.org/project/opensearch-py/) library for connection management and DSL operations, and benefits from all functionality it provides. The only other dependency is Django itself.

Some key advantages to using this app:

- Maintain connections to multiple clusters
- Define all cluster settings, ISM policies, and index template mappings in code, via migration files
  - This make it easier to track and replicate these settings across environments (e.g., dev & prod clusters).
- Run migrations against clusters using Django management commands
  - Under the hood, it tracks the state of migrations in a hidden index in the cluster itself, similar to what Django does using tables in relational dbs.
- Write cleaner unit tests with helpful test runners and mocks

## Quick Start

1. Add this app to your project's list of installed apps:

```python
# settings.py

INSTALLED_APPS = [
    ...
    "django_opensearch_toolkit",
    ...
]
```

2. Define the clusters to configure:

```python
# settings.py

OPENSEARCH_CLUSTERS = {
    "sample_app": {
        "hosts": [
            {
                "host": "localhost",
                "port": 9200,
            }
        ],
        "timeout": 30,
    },
}
```

3. Register migrations for each cluster

```python
# settings.py


OPENSEARCH_MIGRATION_PATHS = {
    # cluster_name -> module_path
    #   - Each module should define a variable named MIGRATIONS.
    #   - The module will be dynamically imported and the MIGRATIONS variable will be used.
    "sample_app": "sample_app.opensearch_migrations",
}
```

NOTE: Currently, we only support a dependency _chain_, instead of a more generic dependency _graph_, like Django does for its migrations.

4. Implement your migrations and ensure they are discoverable at the paths indicated in the previous step. See the `sample_project/sample_app` for an example.

5. Display and run your migrations

```bash
cd sample_project
python manage.py opensearch_displaymigrations sample_app
python manage.py opensearch_runmigrations sample_app
python manage.py opensearch_runmigrations sample_app --nodry
python manage.py opensearch_displaymigrations sample_app
```

## Local Development

From the project root, run:

```bash
./setup.sh                  # Creates a virtual environment in the project directory & downloads all requirements
source venv/bin/activate    # Step into your virtual environment
./run_tests.sh              # Confirm all tests pass
./run_linter.sh             # Confirm all static checks pass
./run_integration_tests.sh  # Run an integration test (requires docker daemon to be running)
deactivate                  # Leave your virtual environment
```
