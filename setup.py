"""Setup script for the Flockwave specification."""

from setuptools import setup, find_packages

requires = [
    "click>=6.2",
    "jsonschema>=2.5.1",
    "memoized>=0.2",
    "warlock>=1.2.0"
]
requires = [line.strip() for line in open("requirements.txt") if not line[0] in '-#']

__version__ = None
exec(open("flockwave/spec/version.py").read())

setup(
    name="flockwave-spec",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    test_suite="test"
)
