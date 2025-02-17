# django-opensearch-toolkit

A Django app to facilitate interacting with OpenSearch clusters, including connection management, migrations, and unit tests.

It is implemented as a thin wrapper over the [opensearch-py](https://pypi.org/project/opensearch-py/) library for connection management and DSL operations, and benefits from all functionality it provides. The only other dependency is Django itself.

Some key advantages to using this app:

- Configure connections to multiple clusters using the Django settings module
    - This is analogous to how Django manages connections to multiple RDBMS databases.
- Define cluster state (e.g., ISM policies, index template mappings, indices) _in code_, via migration files
    - This makes it easier to track and replicate these settings across environments (e.g., dev & prod clusters).
    - This is analogous to how Django generates migration files for schema changes. The difference is that the migrations here are manually written, not auto-generated. They can be written using the DSL of the OpenSearch Python client.
- Run migrations against clusters using Django management commands
    - This is analogous to running `python manage.py migrate` for RDBMS databases.
    - Under the hood, it tracks the state of migrations in a hidden index in the cluster itself to avoid running migrations multiple times, similar to what Django does using tables in relational dbs.
- Write cleaner unit tests with helpful test runners and mocks

## Quick Start

1. Install the package:

```bash
pip install django-opensearch-toolkit
```

2. Add this app to your Django project's list of installed apps:

```python
# settings.py

INSTALLED_APPS = [
    ...
    "django_opensearch_toolkit",
    ...
]
```

3. Define the cluster(s) to configure:

```python
# settings.py

OPENSEARCH_CLUSTERS = {
    # cluster_name -> configuration
    # This dict is passed to opensearchpy.connection.configure() while the
    # Django environment is being initialized.
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

4. Register migrations for each cluster

```python
# settings.py

OPENSEARCH_MIGRATION_PATHS = {
    # cluster_name -> module_path
    #   - Each module should define a variable named MIGRATIONS.
    #   - The module will be dynamically imported and the MIGRATIONS variable will be used.
    "sample_app": "sample_app.opensearch_migrations",
}
```

5. Implement your migrations and ensure they are discoverable at the paths indicated in the previous step. See the `sample_project/sample_app/opensearch_migrations/__init__.py` for an example.

    - **NOTE:** Currently, we only support a dependency _chain_, instead of a more generic dependency _graph_, like Django does for its migrations.

6. Display and run your migrations.

    - This requires a running OpenSearch cluster at localhost:9200 (configured in step 3).

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
./scripts/setup_dev.sh    # Creates a virtual environment in the project directory & downloads all requirements
source venv/bin/activate  # Step into your virtual environment
make test                 # Confirm all tests pass
make check                # Confirm all static checks pass
make integration-test     # Run an integration test (requires docker daemon to be running)
deactivate                # Leave your virtual environment
```
