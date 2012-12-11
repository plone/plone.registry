import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0.1'


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

setup(name='plone.registry',
      version=version,
      description="A debconf-like (or about:config-like) registry for storing application settings",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
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
          'zope.schema',
          'zope.interface',
          'zope.component',
          'zope.dottedname',
          'zope.event',
          'zope.testing',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
