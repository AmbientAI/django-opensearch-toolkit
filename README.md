# django-opensearch-toolkit

A Django app for interacting with OpenSearch clusters, including migrations, search, and unit tests.

## Local Development

From the project root, run:

```
./setup.sh       # Creates a virtual environment in the project directory & downloads all requirments
source venv/bin/activate  # Step into your virtual environment
./run_tests.sh   # Confirm all tests pass
./run_linter.sh  # Confirm all static checks pass
deactivate       # Leave your virtual environment
```

NOTE: As of writing, the `bdist_wheel` command of ElasticMock fails on install. This doesn't impact the tests though.
