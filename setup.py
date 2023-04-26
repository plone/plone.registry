from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = "2.0.0"

description = "Registry for application settings (like debconf/ about:config)"
long_description = (
    read("README.rst")
    + "\n"
    + read("plone", "registry", "registry.rst")
    + "\n"
    + read("plone", "registry", "events.rst")
    + "\n"
    + read("plone", "registry", "field.rst")
    + "\n"
    + read("CHANGES.rst")
    + "\n"
)

setup(
    name="plone.registry",
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="configuration registry",
    author="Martin Aspeli, Wichert Akkerman, Hanno Schlichting",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.registry",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["plone"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "zope.component",
        "zope.dottedname",
        "zope.event",
        "zope.interface",
        "zope.schema",
    ],
    extras_require={"test": ["BTrees", "plone.schema"]},
    entry_points="""
    # -*- Entry points: -*-
    """,
)
