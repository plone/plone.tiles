import unittest

import zope.testing.doctest
import zope.app.testing.placelesssetup

# For directive tests

from zope.interface import Interface
from zope import schema

from plone.tiles import Tile, PersistentTile

class IDummySchema(Interface):
    foo = schema.TextLine(title=u"Foo")

class IDummyContext(Interface):
    pass

class IDummyLayer(Interface):
    pass

class DummyTile(Tile):
    def __call__(self):
        return u"dummy"

class DummyTileWithTemplate(PersistentTile):
    pass

def test_suite():
    return unittest.TestSuite((
        
        zope.testing.doctest.DocFileSuite('tiles.txt',
                     setUp=zope.app.testing.placelesssetup.setUp,
                     tearDown=zope.app.testing.placelesssetup.tearDown),

        zope.testing.doctest.DocFileSuite('directives.txt',
                     setUp=zope.app.testing.placelesssetup.setUp,
                     tearDown=zope.app.testing.placelesssetup.tearDown),

        zope.testing.doctest.DocFileSuite('data.txt',
                     setUp=zope.app.testing.placelesssetup.setUp,
                     tearDown=zope.app.testing.placelesssetup.tearDown),

        ))
