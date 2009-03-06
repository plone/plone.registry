from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.registry',
      version=version,
      description="A debconf-like (or about:config-like) registry for storing application settings",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
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
      license='LGPL',
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
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
