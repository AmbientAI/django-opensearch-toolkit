#/bin/bash
set -e

PYTHONPATH=. python sample_project/manage.py check  --fail-level=WARNING
PYTHONPATH=. python sample_project/manage.py test django_opensearch_toolkit  --verbosity=2
PYTHONPATH=. python sample_project/manage.py test sample_app --verbosity=2