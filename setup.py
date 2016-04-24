# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = '1.6.dev0'

setup(
    name='plone.tiles',
    version=version,
    description="APIs for managing tiles",
    long_description=open("README.rst").read() + "\n" +
    open(os.path.join("plone", "tiles", "tiles.rst")).read() + "\n" +
    open(os.path.join("plone", "tiles", "directives.rst")).read() + "\n" +
    open(os.path.join("plone", "tiles", "esi.rst")).read() + "\n" +
    open("CHANGES.rst").read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.0',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
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
        'test': ['plone.testing [zca, z2]', 'unittest2'],
    },
)
