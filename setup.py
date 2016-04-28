"""Setup script for the Flockwave specification."""

from setuptools import setup, find_packages

requires = [
    "click>=6.2",
    "enum34>=1.1.2",
    "jsonpointer>=1.10",
    "jsonschema>=2.5.1",
    "memoized>=0.2"
]

__version__ = None
exec(open("flockwave/spec/version.py").read())

setup(
    name="flockwave-spec",
    version=__version__,

    author=u"Tam\u00e1s Nepusz",
    author_email="tamas@collmot.com",

    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    install_requires=requires,
    test_suite="test"
)
