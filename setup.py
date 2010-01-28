from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.tiles',
      version=version,
      description="APIs for managing tiles",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("plone", "tiles", "tiles.txt")).read() + "\n" +
                       open(os.path.join("plone", "tiles", "directives.txt")).read() + "\n" +
                       open(os.path.join("plone", "tiles", "esi.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone tiles deco',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/plone.tiles',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.component',
          'zope.schema',
          'zope.publisher',
          'zope.traversing',
          'zope.annotation',
          'zope.configuration',
          'ZODB3',
          'zope.app.publisher',
          'zope.testing',
      ],
      entry_points="""
      """,
      )
