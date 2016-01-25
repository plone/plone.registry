# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0.3.dev0'

description = "Registry for application settings (like debconf/ about:config)"
long_description = (
    read('README.rst')
    + '\n' +
    read('plone', 'registry', 'registry.rst')
    + '\n' +
    read('plone', 'registry', 'events.rst')
    + '\n' +
    read('plone', 'registry', 'field.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n'
    )

setup(
    name='plone.registry',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='configuration registry',
    author='Martin Aspeli, Wichert Akkerman, Hanno Schlichting',
    author_email='plone-developers@lists.sourceforge.net',
    url='http://pypi.python.org/pypi/plone.registry',
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
