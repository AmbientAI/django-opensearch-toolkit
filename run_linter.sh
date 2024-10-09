set -e

flake8 django_opensearch_toolkit
pylint django_opensearch_toolkit

flake8 sample_project
pylint sample_project
