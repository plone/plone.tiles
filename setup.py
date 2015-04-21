import os
from setuptools import setup
from setuptools import find_packages

version = '1.3.0'

setup(
    name='plone.tiles',
    version=version,
    description="APIs for managing tiles",
    long_description=open("README.rst").read() + "\n" +
    open(os.path.join("plone", "tiles", "tiles.rst")).read() + "\n" +
    open(os.path.join("plone", "tiles", "directives.rst")).read() + "\n" +
    open(os.path.join("plone", "tiles", "esi.rst")).read() + "\n" +
    open("CHANGELOG.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone tiles',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='https://github.com/plone/plone.tiles',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.app.publisher',
        'zope.annotation',
        'zope.component',
        'zope.configuration',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        'Zope2',
    ],
    extras_require={
        'test': ['plone.testing [zca, z2]'],
    },
)
