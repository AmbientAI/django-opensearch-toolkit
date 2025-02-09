from setuptools import setup, find_packages

setup(
    name="django-opensearch-toolkit",
    packages=find_packages(
        include=["django_opensearch_toolkit*"],
        exclude=["*/tests/*"],
    ),
    zip_safe=False,
)
