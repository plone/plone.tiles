# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


def read(*path):
    filename = os.path.join(*path)
    with open(filename) as myfile:
        return myfile.read() + '\n'


version = '2.3.0'

setup(
    name='plone.tiles',
    version=version,
    description='APIs for managing tiles',
    long_description=read('README.rst') +
    read('plone', 'tiles', 'tiles.rst') +
    read('plone', 'tiles', 'directives.rst') +
    read('plone', 'tiles', 'esi.rst') +
    read('CHANGES.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 5.1',
        'Framework :: Plone :: 5.2',
        'Framework :: Plone :: Core',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='plone tiles',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='https://github.com/plone/plone.tiles',
    license='GPL version 2',
    packages=find_packages(),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.subrequest',
        'setuptools',
        'zope.annotation',
        'zope.browserpage',
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
        'test': [
            'plone.testing [zca, z2]',
            'plone.rfc822',
        ],
    },
)
