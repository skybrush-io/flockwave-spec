"""Setup script for the Flockwave specification."""

from setuptools import setup, find_packages

requires = [line.strip() for line in open("requirements.txt")]

__version__ = None
exec(open("flockwave/schema/version.py").read())

setup(
    name="flockwave-spec",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    test_suite="test"
)
