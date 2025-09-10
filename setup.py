from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "2.0.2"

description = "Registry for application settings (like debconf/ about:config)"
long_description = (
    f"{Path('README.rst').read_text()}\n"
    f"{(Path('src') / 'plone' / 'registry' / 'registry.rst').read_text()}\n"
    f"{(Path('src') / 'plone' / 'registry' / 'events.rst').read_text()}\n"
    f"{(Path('src') / 'plone' / 'registry' / 'field.rst').read_text()}\n"
    f"{Path('CHANGES.rst').read_text()}"
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
    packages=find_packages("src"),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "Zope",
    ],
    extras_require={"test": ["plone.schema"]},
    entry_points="""
    # -*- Entry points: -*-
    """,
)
