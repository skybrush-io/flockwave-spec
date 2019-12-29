"""Setup script for the Flockwave specification."""

from setuptools import setup, find_packages

requires = ["click>=6.2", "jsonpointer>=2.0", "jsonschema>=3.2.0", "memoized>=0.3.0"]

extra_requires = {}

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
    extras_require=extra_requires,
    test_suite="test",
)
