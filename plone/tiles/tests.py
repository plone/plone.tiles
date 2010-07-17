import unittest2 as unittest
import doctest
from plone.testing import Layer, layered
from plone.testing import zca, z2

from zope.configuration import xmlconfig

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

class PloneTiles(Layer):
    defaultBases = (z2.STARTUP,)

    def setUp(self):
        import plone.tiles
        self['configurationContext'] = context = zca.stackConfigurationContext(self.get('configurationContext'))
        xmlconfig.file('configure.zcml', plone.tiles, context=context)

    def tearDown(self):
        del self['configurationContext']

PLONE_TILES_FIXTURE = PloneTiles()

PLONE_TILES_INTEGRATION_TESTING = z2.IntegrationTesting(bases=(PLONE_TILES_FIXTURE,), name="PloneTiles:Functional")

def test_suite():
    return unittest.TestSuite((        
        layered(doctest.DocFileSuite('tiles.txt', 'directives.txt',
                                     'data.txt', 'esi.txt'),
                layer=PLONE_TILES_INTEGRATION_TESTING),
        ))
