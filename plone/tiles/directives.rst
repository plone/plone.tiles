ZCML directive
==============

A tile is really just a browser view providing ``IBasicTile`` (or, more
commonly, ``ITile`` or ``IPersistentTile``) coupled with a named utility
providing ``ITileType``. The names of the browser view and the tile should
match.

To make it easier to register these components, this package provides a
``<plone:tile />`` directive that sets up both. It supports several use cases:

  * Registering a new tile from a class
  * Registering a new tile from a template only
  * Registering a new tile form a class and a template
  * Registering a new tile for an existing tile type (e.g. for a new layer)

To test this, we have created a dummy schema and a dummy tile in ``tests.py``,
and a dummy template in ``test.pt``.

Let's show how these may be used by registering several tiles::

    >>> configuration = """\
    ... <configure package="plone.tiles"
    ...      xmlns="http://namespaces.zope.org/zope"
    ...      xmlns:plone="http://namespaces.plone.org/plone"
    ...      i18n_domain="plone.tiles.tests">
    ...
    ...     <include package="zope.component" file="meta.zcml" />
    ...     <include package="zope.security" file="meta.zcml" />
    ...     <include package="zope.app.publisher" file="meta.zcml" />
    ...
    ...     <include package="plone.tiles" file="meta.zcml" />
    ...     <include package="plone.tiles" />
    ...
    ...     <permission
    ...         id="plone.tiles.tests.DummyAdd"
    ...         title="Dummy add permission"
    ...         />
    ...     <permission
    ...         id="plone.tiles.tests.DummyView"
    ...         title="Dummy view permission"
    ...         />
    ...
    ...     <!-- A tile configured with all available attributes -->
    ...     <plone:tile
    ...         name="dummy1"
    ...         title="Dummy tile 1"
    ...         description="This one shows all available options"
    ...         add_permission="plone.tiles.tests.DummyAdd"
    ...         schema="plone.tiles.tests.IDummySchema"
    ...         class="plone.tiles.tests.DummyTileWithTemplate"
    ...         template="test.pt"
    ...         for="plone.tiles.tests.IDummyContext"
    ...         layer="plone.tiles.tests.IDummyLayer"
    ...         permission="plone.tiles.tests.DummyView"
    ...         />
    ...
    ...     <!-- A class-only tile -->
    ...     <plone:tile
    ...         name="dummy2"
    ...         title="Dummy tile 2"
    ...         add_permission="plone.tiles.tests.DummyAdd"
    ...         class="plone.tiles.tests.DummyTile"
    ...         for="*"
    ...         permission="plone.tiles.tests.DummyView"
    ...         />
    ...
    ...     <!-- A template-only tile -->
    ...     <plone:tile
    ...         name="dummy3"
    ...         title="Dummy tile 3"
    ...         add_permission="plone.tiles.tests.DummyAdd"
    ...         template="test.pt"
    ...         for="*"
    ...         permission="plone.tiles.tests.DummyView"
    ...         />
    ...
    ...     <!-- Use the PersistentTile class directly with a template-only tile -->
    ...     <plone:tile
    ...         name="dummy4"
    ...         title="Dummy tile 4"
    ...         add_permission="plone.tiles.tests.DummyAdd"
    ...         schema="plone.tiles.tests.IDummySchema"
    ...         class="plone.tiles.PersistentTile"
    ...         template="test.pt"
    ...         for="*"
    ...         permission="plone.tiles.tests.DummyView"
    ...         />
    ...
    ...     <!-- Override dummy3 for a new layer -->
    ...     <plone:tile
    ...         name="dummy3"
    ...         class="plone.tiles.tests.DummyTile"
    ...         for="*"
    ...         layer="plone.tiles.tests.IDummyLayer"
    ...         permission="plone.tiles.tests.DummyView"
    ...         />
    ...
    ... </configure>
    ... """

    >>> from StringIO import StringIO
    >>> from zope.configuration import xmlconfig
    >>> xmlconfig.xmlconfig(StringIO(configuration))

Let's check how the tiles were registered::

    >>> from zope.component import getUtility
    >>> from plone.tiles.interfaces import ITileType

    >>> tile1_type = getUtility(ITileType, name=u"dummy1")
    >>> tile1_type
    <TileType dummy1 (Dummy tile 1)>
    >>> tile1_type.description
    u'This one shows all available options'

    >>> tile1_type.add_permission
    'plone.tiles.tests.DummyAdd'

    >>> tile1_type.view_permission
    'plone.tiles.tests.DummyView'

    >>> tile1_type.schema
    <InterfaceClass plone.tiles.tests.IDummySchema>

    >>> tile2_type = getUtility(ITileType, name=u"dummy2")
    >>> tile2_type
    <TileType dummy2 (Dummy tile 2)>
    >>> tile2_type.description is None
    True
    >>> tile2_type.add_permission
    'plone.tiles.tests.DummyAdd'
    >>> tile2_type.schema is None
    True

    >>> tile3_type = getUtility(ITileType, name=u"dummy3")
    >>> tile3_type
    <TileType dummy3 (Dummy tile 3)>
    >>> tile3_type.description is None
    True
    >>> tile3_type.add_permission
    'plone.tiles.tests.DummyAdd'
    >>> tile3_type.schema is None
    True

    >>> tile4_type = getUtility(ITileType, name=u"dummy4")
    >>> tile4_type
    <TileType dummy4 (Dummy tile 4)>
    >>> tile4_type.description is None
    True
    >>> tile4_type.add_permission
    'plone.tiles.tests.DummyAdd'
    >>> tile4_type.schema
    <InterfaceClass plone.tiles.tests.IDummySchema>

Finally, let's check that we can look up the tiles::

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.interface import implements, alsoProvides

    >>> from plone.tiles.tests import IDummyContext, IDummyLayer

    >>> class Context(object):
    ...     implements(IDummyContext)

    >>> context = Context()
    >>> request = TestRequest()
    >>> layer_request = TestRequest(skin=IDummyLayer)

    >>> from zope.component import getMultiAdapter
    >>> from plone.tiles import Tile, PersistentTile
    >>> from plone.tiles.tests import DummyTile, DummyTileWithTemplate

    >>> tile1 = getMultiAdapter((context, layer_request), name="dummy1")
    >>> isinstance(tile1, DummyTileWithTemplate)
    True
    >>> print tile1()
    <b>test!</b>
    >>> tile1.__name__
    'dummy1'

    >>> tile2 = getMultiAdapter((context, request), name="dummy2")
    >>> isinstance(tile2, DummyTile)
    True
    >>> print tile2()
    dummy
    >>> tile2.__name__
    'dummy2'

    >>> tile3 = getMultiAdapter((context, request), name="dummy3")
    >>> isinstance(tile3, Tile)
    True
    >>> print tile3()
    <b>test!</b>
    >>> tile3.__name__
    'dummy3'

    >>> tile4 = getMultiAdapter((context, request), name="dummy4")
    >>> isinstance(tile4, PersistentTile)
    True
    >>> print tile4()
    <b>test!</b>
    >>> tile4.__name__
    'dummy4'

    >>> tile3_layer = getMultiAdapter((context, layer_request), name="dummy3")
    >>> isinstance(tile3_layer, DummyTile)
    True
    >>> print tile3_layer()
    dummy
    >>> tile3_layer.__name__
    'dummy3'
