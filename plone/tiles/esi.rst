ESI support
===========

Some sites may choose to render tiles in a delayed fashion using Edge Side
Includes or some similar mechanism. ``plone.tiles`` includes some support to
help render ESI placeholders. This is used in ``plone.app.blocks`` to
facilitate ESI rendering. Since ESI normally involves a "dumb" replacement
operation, ``plone.tiles`` also provides a means of accessing just the head
and/or just the body of a tile.

To use the package, you should first load its ZCML configuration.

    >>> configuration = """\
    ... <configure
    ...      xmlns="http://namespaces.zope.org/zope"
    ...      xmlns:plone="http://namespaces.plone.org/plone"
    ...      i18n_domain="plone.tiles.tests">
    ...
    ...     <include package="zope.component" file="meta.zcml" />
    ...     <include package="zope.app.publisher" file="meta.zcml" />
    ...
    ...     <include package="plone.tiles" file="meta.zcml" />
    ...     <include package="plone.tiles" />
    ...
    ... </configure>
    ... """

    >>> from StringIO import StringIO
    >>> from zope.configuration import xmlconfig
    >>> xmlconfig.xmlconfig(StringIO(configuration))

Marking a tile as ESI-rendered
------------------------------

For ESI rendering to be available, the tile must be marked with the
``IESIRendered`` marker interface. We can create a dummy tile with this
interface like so:

    >>> from zope.interface import implements
    >>> from plone.tiles.interfaces import IESIRendered
    >>> from plone.tiles import Tile

    >>> class SampleTile(Tile):
    ...     implements(IESIRendered)
    ...
    ...     __name__ = 'sample.tile' # would normally be set by ZCML handler
    ...
    ...     def __call__(self):
    ...         return "<html><head><title>Title</title></head><body><b>My tile</b></body></html>"

Above, we have created a simple HTML string. This would normally be rendered
using a page template.

We'll register this tile manually here. Ordinarily, of course, it would be
registered via ZCML.

    >>> from plone.tiles.type import TileType
    >>> sampleTileType = TileType(
    ...     name=u'sample.tile',
    ...     title=u"Sample tile",
    ...     description=u"A tile used for testing",
    ...     add_permission="dummy.Permission",
    ...     view_permission="dummy.Permission",
    ...     schema=None)

    >>> from zope.component import provideAdapter, provideUtility
    >>> from zope.interface import Interface
    >>> from plone.tiles.interfaces import IBasicTile

    >>> provideUtility(sampleTileType, name=u'sample.tile')
    >>> provideAdapter(SampleTile, (Interface, Interface), IBasicTile, name=u"sample.tile")

ESI lookup
----------

When a page is rendered (for example by a system like ``plone.app.blocks``,
but see below), a tile placeholder may be replaced by a link such as::

    <esi:include src="/path/to/context/@@sample.tile/tile1/@@esi-body" />

When this is resolved, it will return the body part of the tile. Equally,
a tile in the head can be replaced by::

    <esi:include src="/path/to/context/@@sample.tile/tile1/@@esi-head" />

To illustrate how this works, let's create a sample context, look up the view
as it would be during traversal, and instantiate the tile, before looking up
the ESI views and rendering them.

    >>> from zope.interface import implements

    >>> class IContext(Interface):
    ...     pass

    >>> class Context(object):
    ...     implements(IContext)

    >>> from zope.publisher.browser import TestRequest

    >>> class IntegratedTestRequest(TestRequest):
    ...     @property
    ...     def environ(self):
    ...         return self._environ

    >>> context = Context()
    >>> request = IntegratedTestRequest()

    >>> from zope.interface import Interface
    >>> from zope.component import getMultiAdapter

The following simulates traversal to ``context/@@sample.tile/tile1``

    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> tile = tile['tile1'] # simulates sub-path traversal

This tile should be ESI rendered::

    >>> IESIRendered.providedBy(tile)
    True

At this point, we can look up the ESI views:

    >>> head = getMultiAdapter((tile, request), name="esi-head")
    >>> print head()
    <title>Title</title>

    >>> body = getMultiAdapter((tile, request), name="esi-body")
    >>> print body()
    <b>My tile</b>

Tiles without heads or bodies
-----------------------------

In general, tiles are supposed to return full HTML documents. The ``esi-head``
and ``esi-body`` views are tolerant of tiles that do not. If they cannot find
a ``<head />`` or ``<body />`` element, respectively, they will return the
underlying tile output unaltered.

For example:

    >>> from plone.tiles.esi import ESITile
    >>> class LazyTile(ESITile):
    ...     __name__ = 'sample.esi1' # would normally be set by ZCML handler
    ...     def __call__(self):
    ...         return "<title>Page title</title>"

We won't bother to register this for this test, instead just instantiating
it directly:

    >>> tile = LazyTile(context, request)['tile1']

    >>> IESIRendered.providedBy(tile)
    True

    >>> head = getMultiAdapter((tile, request), name="esi-head")
    >>> print head()
    <title>Page title</title>

Of course, the ESI body renderer would return the same thing, since it can't
extract a specific body either:

    >>> body = getMultiAdapter((tile, request), name="esi-body")
    >>> print body()
    <title>Page title</title>

In this case, we would likely end up with invalid HTML, since the
``<title />`` tag is not allowed in the body. Whether and how to resolve
this is left up to the ESI interpolation implementation.

Convenience classes and placeholder rendering
---------------------------------------------

Two convenience base classes can be found in the ``plone.tiles.esi`` module.
These extend the standard ``Tile`` and ``PersistentTile`` classes
to provide the ``IESIRendered`` interface.

* ``plone.tiles.esi.ESITile``, a transient, ESI-rendered tile
* ``plone.tiles.esi.ESIPersistentTile``, a persistent, ESI-rendered tile

These are particularly useful if you are creating a template-only tile and
want ESI rendering. For example::

    <plone:tile
        name="sample.esitile"
        title="An ESI-rendered tile"
        add_permission="plone.tiles.tests.DummyAdd"
        template="esitile.pt"
        class="plone.tiles.esi.ESITile"
        for="*"
        permission="zope.View"
        />

Additionally, these base classes implement a ``__call__()`` method that will
render a tile placeholder if the request contains an ``X-ESI-Enabled``
header set to the literal 'true'.

The placeholder is a simple HTML ``<a />`` tag, which can be transformed into
an ``<esi:include />`` tag using the helper function ``substituteESILinks()``.
The reason for this indirection is that the ``esi`` namespace is not allowed
in HTML documents and are liable to be stripped out by transforms using the
``libxml2`` / ``lxml`` HTML parser.

Let us now create a simple ESI tile. To benefit from the default rendering,
we should implement the ``render()`` method instead of ``__call__()``. Setting
a page template as the ``index`` class variable or using the ``template``
attribute to the ZCML directive will work also.

    >>> from plone.tiles.esi import ESITile

    >>> class SampleESITile(ESITile):
    ...     __name__ = 'sample.esitile' # would normally be set by ZCML handler
    ...
    ...     def render(self):
    ...         return "<html><head><title>Title</title></head><body><b>My ESI tile</b></body></html>"

    >>> sampleESITileType = TileType(
    ...     name=u'sample.esitile',
    ...     title=u"Sample ESI tile",
    ...     description=u"A tile used for testing ESI",
    ...     add_permission="dummy.Permission",
    ...     view_permission="dummy.Permission",
    ...     schema=None)

    >>> provideUtility(sampleESITileType, name=u'sample.esitile')
    >>> provideAdapter(SampleESITile, (Interface, Interface), IBasicTile, name=u"sample.esitile")

The following simulates traversal to ``context/@@sample.esitile/tile1``

    >>> tile = getMultiAdapter((context, request), name=u"sample.esitile")
    >>> tile = tile['tile1'] # simulates sub-path traversal

By default, the tile renders as normal:

    >>> print tile()
    <html><head><title>Title</title></head><body><b>My ESI tile</b></body></html>

However, if we opt into ESI rendering via a request header, we get a different
view:

    >>> from plone.tiles.interfaces import ESI_HEADER_KEY
    >>> request.environ[ESI_HEADER_KEY] = 'true'
    >>> print tile() # doctest: +NORMALIZE_WHITESPACE
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
            <a class="_esi_placeholder"
               rel="esi"
               href="http://127.0.0.1/@@esi-body?"></a>
        </body>
    </html>

This can be transformed into a proper ESI tag with ``substituteESILinks()``:

    >>> from plone.tiles.esi import substituteESILinks
    >>> print substituteESILinks(tile()) # doctest: +NORMALIZE_WHITESPACE
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns:esi="http://www.edge-delivery.org/esi/1.0" xmlns="http://www.w3.org/1999/xhtml">
        <body>
            <esi:include src="http://127.0.0.1/@@esi-body?" />
        </body>
    </html>

It is also possible to render the ESI tile for the head. This is done with
a class variable 'head' (which would of course normally be set within the
class):

    >>> SampleESITile.head = True
    >>> print tile() # doctest: +NORMALIZE_WHITESPACE
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
            <a class="_esi_placeholder"
               rel="esi"
               href="http://127.0.0.1/@@esi-head?"></a>
        </body>
    </html>
