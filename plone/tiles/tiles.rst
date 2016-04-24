Tiles in detail
===============

Tiles are a form of view component used to compose pages. Think of a tile as
a view describing one part of a page, that can be configured with some data
described by a schema and inserted into a layout via a dedicated GUI.

Like a browser view, a tile can be traversed to and published on its own. The
tile should then return a full HTML page, including a <head /> with any
required resources, and a <body /> with the visible part of the tile. This
will then be merged into the page, using a system such as
``plone.app.blocks``.

The API in this package provides support for tiles being configured according
to a schema with data either passed on the query string (transient tiles) or
retrieved from annotations (persistent tiles).

Note that there is no direct UI support in this package, so the forms that
allow users to construct and edit tiles must live elsewhere. You may be
interested in ``plone.app.tiles`` and ``plone.app.deco`` for that purpose.

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

A simple transient tile
-----------------------

A basic tile is a view that implements the ``ITile`` interface. The easiest
way to do this is to subclass the ``Tile`` class.

    >>> from plone.tiles import Tile
    >>> class SampleTile(Tile):
    ...
    ...     __name__ = 'sample.tile' # would normally be set by ZCML handler
    ...
    ...     def __call__(self):
    ...         return "<html><body><b>My tile</b></body></html>"

The tile is a browser view:

    >>> from plone.tiles.interfaces import ITile
    >>> ITile.implementedBy(SampleTile)
    True

    >>> from zope.publisher.interfaces.browser import IBrowserView
    >>> IBrowserView.implementedBy(SampleTile)
    True

The tile instance has a ``__name__`` attribute (normally set at class level
by the ``<plone:tile />`` ZCML directive), as well as a property ``id``. The
id may be set explicitly, either in code, or by sub-path traversal. For
example, if the tile name is ``example.tile``, the id may be set to ``tile1``
using a URL like ``http://example.com/foo/@@example.tile/tile1``.

This tile is registered as a normal browser view, alongside a utility that
provides some information about the tile itself. Normally, this is done
using the ``<plone:tile />`` directive. Here's how to create one manually:

    >>> from plone.tiles.type import TileType
    >>> sampleTileType = TileType(
    ...     u'sample.tile',
    ...     u"Sample tile",
    ...     "dummy.Permission",
    ...     "dummy.Permission",
    ...     description=u"A tile used for testing",
    ...     schema=None)

The name should match the view name and the name the utility is registered
under. The title and description may be used by the UI. The add permission
is the name of a permission that will be required to insert the tile. The
schema attribute may be used to indicate schema interface describing the
tile's configurable data - more on this below.

To register a tile in ZCML, we could do::

    <plone:tile
        name="sample.tile"
        title="Sample tile"
        description="A tile used for testing"
        add_permission="dummy.Permission"
        class=".mytiles.SampleTile"
        for="*"
        permission="zope.Public"
        />

**Note:** The tile name should be a dotted name, prefixed by a namespace you
control. It's a good idea to use a package name for this purpose.

It is also possible to specify a ``layer`` or ``template`` like the
``browser:page`` directive, as well as a ``schema``, which we will describe
below.

We'll register the sample tile directly here, for later testing.

    >>> from zope.component import provideAdapter, provideUtility
    >>> from zope.interface import Interface
    >>> from plone.tiles.interfaces import IBasicTile

    >>> provideUtility(sampleTileType, name=u'sample.tile')
    >>> provideAdapter(SampleTile, (Interface, Interface), IBasicTile, name=u"sample.tile")

Tile traversal
--------------

Tiles are publishable as a normal browser view. They will normally be called
with a sub-path that specifies a tile id. This allows tiles to be made aware
of their instance name. The id is unique within the page layout where the tile
is used, and may be the basis for looking up tile data.

For example, a tile may be saved in a layout as a link like::

    <link rel="tile" target="mytile" href="./@@sample.tile/tile1" />

(The idea here is that the tile link tells the rendering algorithm to replace
the element with id ``mytile`` with the body of the rendered tile - see
``plone.app.blocks`` for details).

Let's create a sample context, look up the view as it would be during
traversal, and verify how the tile is instantiated.

    >>> from zope.interface import implements

    >>> class IContext(Interface):
    ...     pass

    >>> class Context(object):
    ...     implements(IContext)

    >>> from zope.publisher.browser import TestRequest

    >>> context = Context()
    >>> request = TestRequest()

    >>> from zope.interface import Interface
    >>> from zope.component import getMultiAdapter

    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> tile = tile['tile1'] # simulates sub-path traversal

The tile will now be aware of its name and id:

    >>> isinstance(tile, SampleTile)
    True
    >>> tile.__parent__ is context
    True
    >>> tile.id
    'tile1'
    >>> tile.__name__
    'sample.tile'

The sub-path traversal is implemented using a custom ``__getitem__()`` method.
To look up a view on a tile, you can traverse to it *after* you've traversed
to the id sub-path:

    >>> from zope.interface import Interface
    >>> from zope.component import adapts
    >>> from zope.publisher.browser import BrowserView
    >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
    >>> class TestView(BrowserView):
    ...     adapts(SampleTile, IDefaultBrowserLayer)
    ...     def __call__(self):
    ...         return "Dummy view"
    >>> provideAdapter(TestView, provides=Interface, name="test-view")

    >>> tile.id is not None
    True
    >>> tile['test-view']()
    'Dummy view'

If there is no view and we have an id already, we will get a ``KeyError``:

    >>> tile['not-known'] # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    KeyError: 'not-known'

To ensure consistency with Zope's various tangles publication machines, it
is also possible to traverse using the ``publishTraverse`` method::

    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> tile = tile.publishTraverse(request, 'tile1') # simulates sub-path traversal

    >>> isinstance(tile, SampleTile)
    True
    >>> tile.__parent__ is context
    True
    >>> tile.id
    'tile1'
    >>> tile.__name__
    'sample.tile'

Transient tile data
-------------------

Let us now consider how tiles may have data. In the simplest case, tile
data is passed on the query string, and described according to a schema.
A simple schema may look like:

    >>> import zope.schema
    >>> class ISampleTileData(Interface):
    ...     title = zope.schema.TextLine(title=u"Tile title")
    ...     cssClass = zope.schema.ASCIILine(title=u"CSS class to apply")
    ...     count = zope.schema.Int(title=u"Number of things to show in the tile")

We would normally have listed this interface when registering this tile in
ZCML. We can simply update the utility here.

    >>> sampleTileType.schema = ISampleTileData

Tile data is represented by a simple dictionary. For example:

    >>> data = {'title': u"My title", 'count': 5, 'cssClass': 'foo'}

The idea is that a tile add form is built from the schema interface, and its
data saved to a dictionary.

For transient tiles, this data is then encoded into the tile query string. To
help with this, a utility function can be used to encode a dict to a query
string, applying Zope form marshalers according to the types described in
the schema:

    >>> from plone.tiles.data import encode
    >>> encode(data, ISampleTileData)
    'title=My+title&cssClass=foo&count%3Along=5'

The ``count%3Along=5`` bit is the encoded version of ``count:long=5``.

Note that not all field types may be saved. In particular, object, interface,
set or frozen set fields may not be saved, and will result in a ``KeyError``.
Lengthy text fields or bytes fields with binary data may also be a problem.
For these types of fields, look to use persistent tiles instead.

Furthermore, the conversion may not be perfect. For example, Zope's form
marshalers cannot distinguish between unicode and ascii fields. Therefore,
there is a corresponding ``decode()`` method that may be used to ensure that
the values match the schema:

    >>> marshaled = {'title': u"My tile", 'count': 5, 'cssClass': u'foo'}

    >>> from plone.tiles.data import decode
    >>> decode(marshaled, ISampleTileData)
    {'count': 5, 'cssClass': 'foo', 'title': u'My tile'}

When saved into a layout, the tile link would now look like::

    <link rel="tile" target="mytile"
      href="./@@sample.tile/tile1?title=My+title&count%3Along=5&cssClass=foo" />

Let's simulate traversal once more and see how the data is now available to
the tile instance:

    >>> context = Context()
    >>> request = TestRequest(form={'title': u'My title', 'count': 5, 'cssClass': u'foo'})

    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> tile = tile['tile1']

    >>> sorted(tile.data.items())
    [('count', 5), ('cssClass', 'foo'), ('title', u'My title')]

Notice also how the data has been properly decoded according to the schema.

Transient tiles will get their data directly from the request
parameters but, if a `_tiledata` JSON-encoded parameter is present in
the request, this one will be used instead::

    >>> try:
    ...     import json
    ... except ImportError:
    ...     import simplejson as json

    >>> request = TestRequest(form={
    ...     'title': u'My title', 'count': 5, 'cssClass': u'foo',
    ...     '_tiledata': json.dumps({'title': u'Your title', 'count': 6, 'cssClass': u'bar'})
    ...     })
    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> tile = tile['tile1']

    >>> sorted(tile.data.items())
    [(u'count', 6), (u'cssClass', u'bar'), (u'title', u'Your title')]

This way we can use transient tiles safely in contexts where the tile
data can be confused with raw data coming from a form, e.g. in an edit form.

The tile data manager
---------------------

The ``data`` attribute is a convenience attribute to get hold of a (cached)
copy of the data returned by an ``ITileDataManager``. This interface provides
three methods: ``get()``, to return the tile's data, ``set()``, to update it
with a new dictionary of data, and ``delete()``, to delete the data.

This adapter is mostly useful for writing UI around tiles. Using our tile
above, we can get the data like so:

    >>> from plone.tiles.interfaces import ITileDataManager
    >>> dataManager = ITileDataManager(tile)
    >>> dataManager.get() == tile.data
    True

We can also update the tile data:

    >>> dataManager.set({'count': 1, 'cssClass': 'bar', 'title': u'Another title'})
    >>> sorted(dataManager.get().items())
    [('count', 1), ('cssClass', 'bar'), ('title', u'Another title')]

The data can also be deleted:

    >>> dataManager.delete()
    >>> sorted(dataManager.get().items())
    [('count', None), ('cssClass', None), ('title', None)]

Note that in the case of a transient tile, all we are doing is
modifying the ``form`` dictionary of the request (or the `_tiledata`
parameter of this dictionary, if present). The data needs to be
encoded into the query string, either using the ``encode()`` method or
via the tile's ``IAbsoluteURL`` adapter (see below for details).

For persistent tiles, the data manager is a bit more interesting.

Persistent tiles
----------------

Not all types of data can be placed in a query string. For more substantial
storage requirements, you can use persistent tiles, which store data in
annotations.

*Note:* If you have more intricate requirements, you can also write your own
``ITileDataManager`` to handle data retrieval. In this case, you probably
still want to derive from ``PersistentTile``, to get the appropriate
``IAbsoluteURL`` adapter, among other things.

First, we need to write up annotations support.

    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> provideAdapter(AttributeAnnotations)

We also need a context that is annotatable.

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zope.interface import alsoProvides
    >>> alsoProvides(context, IAttributeAnnotatable)

Now, let's create a persistent tile with a schema.

    >>> class IPersistentSampleData(Interface):
    ...     text = zope.schema.Text(title=u"Detailed text", missing_value=u"Missing!")

    >>> from plone.tiles import PersistentTile
    >>> class PersistentSampleTile(PersistentTile):
    ...
    ...     __name__ = 'sample.persistenttile' # would normally be set by ZCML handler
    ...
    ...     def __call__(self):
    ...         return u"<b>You said</b> %s" % self.data['text']

    >>> persistentSampleTileType = TileType(
    ...     u'sample.persistenttile',
    ...     u"Persistent sample tile",
    ...     "dummy.Permission",
    ...     "dummy.Permission",
    ...     description=u"A tile used for testing",
    ...     schema=IPersistentSampleData)

    >>> provideUtility(persistentSampleTileType, name=u'sample.persistenttile')
    >>> provideAdapter(PersistentSampleTile, (Interface, Interface), IBasicTile, name=u"sample.persistenttile")

We can now traverse to the tile as before. By default, there is no data, and
the field's missing value will be used.

    >>> request = TestRequest()

    >>> tile = getMultiAdapter((context, request), name=u"sample.persistenttile")
    >>> tile = tile['tile2']
    >>> tile.__name__
    'sample.persistenttile'
    >>> tile.id
    'tile2'

    >>> tile()
    u'<b>You said</b> Missing!'

At this point, there is nothing in the annotations for the type either:

    >>> dict(getattr(context, '__annotations__', {})).keys()
    []

We can write data to the context's annotations using an ``ITileDataManager``:

    >>> dataManager = ITileDataManager(tile)
    >>> dataManager.set({'text': u"Hello!"})

This writes data to annotations:

    >>> dict(context.__annotations__).keys()
    [u'plone.tiles.data.tile2']
    >>> context.__annotations__[u'plone.tiles.data.tile2']
    {'text': u'Hello!'}

We can get this from the data manager too, of course:

    >>> dataManager.get()
    {'text': u'Hello!'}

Note that as with transient tiles, the ``data`` attribute is cached and will
only be looked up once.

If we now look up the tile again, we will get the new value:

    >>> tile = getMultiAdapter((context, request), name=u"sample.persistenttile")
    >>> tile = tile['tile2']
    >>> tile()
    u'<b>You said</b> Hello!'

    >>> tile.data
    {'text': u'Hello!'}

We can also remove the annotation using the data manager:

    >>> dataManager.delete()
    >>> sorted(dict(context.__annotations__).items()) # doctest: +ELLIPSIS
    []


Overriding transient data with persistent
-----------------------------------------

To be able to re-use the same centrally managed tile based layouts for
multiple context objects, but still allow optional customization for
tiles, it's possible to override otherwise transient tile configuration
with context specific persistent configuration.

This is done by either by setting a client side request header or query param
``X-Tile-Persistent``:

    >>> request = TestRequest(
    ...     form={'title': u'My title', 'count': 5, 'cssClass': u'foo',
    ...           'X-Tile-Persistent': 'yes'}
    ... )

Yet, just adding the flag, doesn't create new persistent annotations
on GET requests:

    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> ITileDataManager(tile)
    <plone.tiles.data.PersistentTileDataManager object at ...>

    >>> sorted(ITileDataManager(tile).get().items(), key=lambda x: x[0])
    [('count', 5), ('cssClass', 'foo'), ('title', u'My title')]

    >>> from zope.annotation.interfaces import IAnnotations
    >>> list(IAnnotations(context).keys())
    []

That's because the data is persistent only once it's set:

    >>> data = ITileDataManager(tile).get()
    >>> data.update({'count': 6})
    >>> ITileDataManager(tile).set(data)
    >>> list(IAnnotations(context).keys())
    [u'plone.tiles.data...']

    >>> sorted(IAnnotations(context).values()[0].items(), key=lambda x: x[0])
    [('count', 6), ('cssClass', 'foo'), ('title', u'My title')]

    >>> sorted(ITileDataManager(tile).get().items(), key=lambda x: x[0])
    [('count', 6), ('cssClass', 'foo'), ('title', u'My title')]

Without the persistent flag, fixed transient data would be returned:

    >>> request = TestRequest(
    ...     form={'title': u'My title', 'count': 5, 'cssClass': u'foo'},
    ... )
    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> ITileDataManager(tile)
    <plone.tiles.data.TransientTileDataManager object at ...>

    >>> data = ITileDataManager(tile).get()
    >>> sorted(data.items(), key=lambda x: x[0])
    [('count', 5), ('cssClass', 'foo'), ('title', u'My title')]

Finally, the persistent override could also be deleted:

    >>> request = TestRequest(
    ...     form={'title': u'My title', 'count': 5, 'cssClass': u'foo',
    ...           'X-Tile-Persistent': 'yes'}
    ... )
    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> ITileDataManager(tile)
    <plone.tiles.data.PersistentTileDataManager object at ...>

    >>> sorted(ITileDataManager(tile).get().items(), key=lambda x: x[0])
    [('count', 6), ('cssClass', 'foo'), ('title', u'My title')]

    >>> ITileDataManager(tile).delete()
    >>> list(IAnnotations(context).keys())
    []

    >>> sorted(ITileDataManager(tile).get().items(), key=lambda x: x[0])
    [('count', 5), ('cssClass', 'foo'), ('title', u'My title')]

    >>> request = TestRequest(
    ...     form={'title': u'My title', 'count': 5, 'cssClass': u'foo'},
    ... )
    >>> tile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> ITileDataManager(tile)
    <plone.tiles.data.TransientTileDataManager object at ...>


Tile URLs
---------

As we have seen, tiles have a canonical URL. For transient tiles, this may
also encode some tile data.

If you have a tile instance and you need to know the canonical tile URL,
you can use the ``IAbsoluteURL`` API.

For the purposes of testing, we need to ensure that we can get an absolute URL
for the context. We'll achieve that with a dummy adapter:

    >>> from zope.interface import implements
    >>> from zope.component import adapts

    >>> from zope.traversing.browser.interfaces import IAbsoluteURL
    >>> from zope.publisher.interfaces.http import IHTTPRequest

    >>> class DummyAbsoluteURL(object):
    ...     implements(IAbsoluteURL)
    ...     adapts(IContext, IHTTPRequest)
    ...
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...         self.request = request
    ...
    ...     def __unicode__(self):
    ...         return u"http://example.com/context"
    ...     def __str__(self):
    ...         return u"http://example.com/context"
    ...     def __call__(self):
    ...         return self.__str__()
    ...     def breadcrumbs(self):
    ...         return ({'name': u'context', 'url': 'http://example.com/context'},)
    >>> provideAdapter(DummyAbsoluteURL, name=u"absolute_url")
    >>> provideAdapter(DummyAbsoluteURL)

    >>> from zope.traversing.browser.absoluteurl import absoluteURL
    >>> from zope.component import getMultiAdapter

    >>> context = Context()
    >>> request = TestRequest(form={'title': u'My title', 'count': 5, 'cssClass': u'foo'})
    >>> transientTile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> transientTile = transientTile['tile1']

    >>> absoluteURL(transientTile, request)
    'http://example.com/context/@@sample.tile/tile1?title=My+title&cssClass=foo&count%3Along=5'

    >>> getMultiAdapter((transientTile, request), IAbsoluteURL).breadcrumbs() == \
    ... ({'url': 'http://example.com/context', 'name': u'context'},
    ...  {'url': 'http://example.com/context/@@sample.tile/tile1', 'name': 'sample.tile'})
    True

For convenience, the tile URL is also available under the ``url`` property:

    >>> transientTile.url
    'http://example.com/context/@@sample.tile/tile1?title=My+title&cssClass=foo&count%3Along=5'

The tile absolute URL structure remains unaltered if the data is
coming from a `_tiledata` JSON-encoded parameter instead of from the request
parameters directly::

    >>> request = TestRequest(form={'_tiledata': json.dumps({'title': u'Your title', 'count': 6, 'cssClass': u'bar'})})
    >>> transientTile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> transientTile = transientTile['tile1']

    >>> absoluteURL(transientTile, request)
    'http://example.com/context/@@sample.tile/tile1?title=Your+title&cssClass=bar&count%3Along=6'

For persistent tiles, the are no data parameters:

    >>> context = Context()
    >>> request = TestRequest(form={'title': u'Ignored', 'count': 0, 'cssClass': u'ignored'})
    >>> persistentTile = getMultiAdapter((context, request), name=u"sample.persistenttile")
    >>> persistentTile = persistentTile['tile2']

    >>> absoluteURL(persistentTile, request)
    'http://example.com/context/@@sample.persistenttile/tile2'

    >>> getMultiAdapter((persistentTile, request), IAbsoluteURL).breadcrumbs() == \
    ... ({'url': 'http://example.com/context', 'name': u'context'},
    ...  {'url': 'http://example.com/context/@@sample.persistenttile/tile2', 'name': 'sample.persistenttile'})
    True

And again, for convenience:

    >>> persistentTile.url
    'http://example.com/context/@@sample.persistenttile/tile2'

If the tile doesn't have an id, we don't get any sub-path

    >>> request = TestRequest(form={'title': u'My title', 'count': 5, 'cssClass': u'foo'})
    >>> transientTile = getMultiAdapter((context, request), name=u"sample.tile")
    >>> absoluteURL(transientTile, request)
    'http://example.com/context/@@sample.tile?title=My+title&cssClass=foo&count%3Along=5'

    >>> request = TestRequest()
    >>> persistentTile = getMultiAdapter((context, request), name=u"sample.persistenttile")
    >>> absoluteURL(persistentTile, request)
    'http://example.com/context/@@sample.persistenttile'
