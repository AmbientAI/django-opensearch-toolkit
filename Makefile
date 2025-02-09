############################################################
# Top-Level Makefile for the django-opensearch-toolkit repo
############################################################

all: default
default: install_requirements test


############################################################################
# Environment Setup
############################################################################

.PHONY: upgrade_pip
upgrade_pip:
	pip install --upgrade pip


.PHONY: install_base_requirements
install_base_requirements: upgrade_pip
	pip install -r requirements.txt


.PHONY: install_dev_requirements
install_dev_requirements: upgrade_pip
	pip install -r requirements_dev.txt


.PHONY: install_requirements
install_requirements: install_base_requirements install_dev_requirements


############################################################################
# Testing
############################################################################

.PHONY: test
test:
	PYTHONPATH=. python sample_project/manage.py check  --fail-level=WARNING
	PYTHONPATH=. python sample_project/manage.py test django_opensearch_toolkit  --verbosity=2
	PYTHONPATH=. python sample_project/manage.py test sample_app --verbosity=2


.PHONY: integration-test
integration-test:
	bash ./scripts/integration_test_helper.sh start
	bash ./scripts/integration_test_helper.sh check
	bash ./scripts/integration_test_helper.sh stop


############################################################################
# Static Analysis
############################################################################

.PHONY: check
check:
	black --check django_opensearch_toolkit
	black --check sample_project
	flake8 django_opensearch_toolkit
	flake8 sample_project
	mypy django_opensearch_toolkit
	mypy sample_project
