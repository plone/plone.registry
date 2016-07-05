# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1.0'

description = "Registry for application settings (like debconf/ about:config)"
long_description = (
    read('README.rst') +
    '\n' +
    read('plone', 'registry', 'registry.rst') +
    '\n' +
    read('plone', 'registry', 'events.rst') +
    '\n' +
    read('plone', 'registry', 'field.rst') +
    '\n' +
    read('CHANGES.rst') +
    '\n'
)

setup(
    name='plone.registry',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='configuration registry',
    author='Martin Aspeli, Wichert Akkerman, Hanno Schlichting',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/plone.registry',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'ZODB3',
        'zope.component',
        'zope.dottedname',
        'zope.event',
        'zope.interface',
        'zope.schema',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
