# -*- coding: utf-8 -*-

from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca
from plone.tiles import PersistentTile
from plone.tiles import Tile
from zope import schema
from zope.configuration import xmlconfig
from zope.interface import Interface


# For directive tests

class IDummySchema(Interface):
    foo = schema.TextLine(title=u'Foo')


class IDummyContext(Interface):
    pass


class IDummyLayer(Interface):
    pass


class DummyTile(Tile):

    def __call__(self):
        return u'dummy'


class DummyTileWithTemplate(PersistentTile):
    pass


class PloneTiles(Layer):
    defaultBases = (z2.STARTUP,)

    def setUp(self):
        self['configurationContext'] = context = zca.stackConfigurationContext(
            self.get('configurationContext')
        )
        import zope.annotation
        xmlconfig.file('configure.zcml', zope.annotation, context=context)
        import plone.tiles
        xmlconfig.file('configure.zcml', plone.tiles, context=context)

    def tearDown(self):
        del self['configurationContext']


PLONE_TILES_FIXTURE = PloneTiles()


PLONE_TILES_INTEGRATION_TESTING = z2.IntegrationTesting(
    bases=(PLONE_TILES_FIXTURE,),
    name='PloneTiles:Functional'
)
