#/bin/bash
set -e

flake8 django_opensearch_toolkit
mypy django_opensearch_toolkit

flake8 sample_project
mypy sample_project
