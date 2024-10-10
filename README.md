# django-opensearch-toolkit

A Django app for interacting with OpenSearch clusters, including migrations, search, and unit tests.

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

NOTE: make sure it is discoverable via the `PYTHONPATH`.

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
PYTHONPATH=../ python manage.py opensearch_displaymigrations sample_app
PYTHONPATH=../ python manage.py opensearch_runmigrations sample_app
PYTHONPATH=../ python manage.py opensearch_runmigrations sample_app --nodry
PYTHONPATH=../ python manage.py opensearch_displaymigrations sample_app
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

NOTE: As of writing, the `bdist_wheel` command of ElasticMock fails on install. This doesn't impact the tests though.
