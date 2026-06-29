"""Package configuration for the Module 5 Grad Cafe Analytics project."""

from setuptools import find_packages, setup


setup(
    name="grad-cafe-analytics-module-5",
    version="0.1.0",
    description="Secure Grad Cafe analytics application for Module 5.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "psycopg",
        "flask",
    ],
)