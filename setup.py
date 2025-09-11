from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "3.0.3"

tiles_path = Path("src") / "plone" / "tiles"

setup(
    name="plone.tiles",
    version=version,
    description="APIs for managing tiles",
    long_description=(
        f"{Path('README.rst').read_text()}\n"
        f"{(tiles_path / 'tiles.rst').read_text()}\n"
        f"{(tiles_path / 'directives.rst').read_text()}\n"
        f"{(tiles_path / 'esi.rst').read_text()}\n"
        f"{Path('CHANGES.rst').read_text()}\n"
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone tiles",
    author="Martin Aspeli",
    author_email="optilude@gmail.com",
    url="https://github.com/plone/plone.tiles",
    license="GPL version 2",
    packages=find_packages("src"),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "plone.subrequest",
        "setuptools",
        "zope.annotation",
        "zope.component",
        "zope.configuration",
        "zope.interface",
        "zope.publisher",
        "zope.schema",
        "zope.security",
        "zope.traversing",
        "plone.protect",
        "plone.supermodel",
        "Zope",
    ],
    extras_require={
        "test": [
            "plone.testing [zca, z2]",
            "plone.rfc822",
        ],
    },
)
