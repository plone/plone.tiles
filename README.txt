Introduction
============

plone.tiles implements low-level, non-Plone/Zope2-specific support for
creating "tiles" in the Deco layout system.

.. contents:: Table of contents

For the purposes of this package, a tile is a browser view and an associated
utility providing some metadata about that view. The metadata includes a title
and description, an 'add' permission and optionally a schema interface
describing configurable aspects of the tile. The idea is that a UI (such as
Deco) can present the user with a list of insertable tiles and optionally
render a form to configure the tile upon insertion.

A tile is inserted into a layout as a link::

    <link rel="tile" target="placeholder" href="./@@sample.tile/tile1?option1=value1" />

The sub-path (`tile1`` in this case) is used to set the tile `id` attribute.
This allows the tile to know its unique id, and, in the case of persistent
tiles, look up its data. `sample.tile` is the name of the browser view that
implements the tile. This is made available as the `__name__` attribute. Other
parameters may be turned into tile data, available under the `data` attribute,
a dict, for regular tiles. For persistent tiles (those deriving from the
`PersistentTile` base class), the data is fetched from annotations instead,
based on the tile id.

There are three interfaces describing tiles in this package:

* `IBasicTile` is the low-level interface for tiles. It extends
  `IBrowserView` to describe the semantics of the `__name__` and  `id`
  attributes.
* `ITile` describes a tile that can be configured with some data. The data
  is accessible via a dict called `data`. The default implementation of this
  interface, `plone.tiles.Tile`, will use the schema of the tile type and
  the query string (`self.request.form`) to construct that dictionary. This
  interface also describes an attribute `url`, which gives the canonical
  tile URL, including the id sub-path and any query string parameters. (Note
  that tiles also correctly implement `IAbsoluteURL`.)
* `IPersistentTile` describes a tile that stores its configuration in
  object annotations, and is needed when configuration values cannot be
  encoded into a query string. The default implementation is in
  `plone.tiles.PersistentTile`. To make it possible to have several tiles
  of a given type on the same layout, the annotations are keyed by the
  tile `__name__`.

In addition, tiles are described by `ITileType`, which contains attributes
for the tile name, title, description, add permission and schema (if 
required).

A properly configured tile, then, consists of a browser view providing
`IBasicTile` or one of its derivatives, and a utility providing `ITileType`
with the same name as the tile browser view. There is a convenience ZCML
directive - `<plone:tile />` - to register both of these components in one
go.

To support creation of appropriate tile links, `plone.tiles.data` contains two
methods - `encode()` and `decode()` - to help turn a data dictionary into a
query string and turn a `request.form` dict into a data dict that complies
with a tile's schema interface.

Creating a simple tile
======================

The most basic tile looks like this::

    from plone.tiles import Tile
    
    class MyTile(Tile):
        
        def __call__(self):
            return u"<html><body><p>Hello world</p></body></html>"

Note that the tile is expected to return a complete HTML document. This will
be interpolated into the page output according to the following rules:

* The contents of the tile's ``<head />`` section is appended to the output
  document's ``<head />`` section.
* The contents of the tile's ``<body />`` section will replace the tile
  placeholder as indicated by the tile link.
  
Note that this package does *not* provide these interpolations. For a Plone
implementation of the interpolation algorithm, see `plone.app.blocks`_

If you require a persistent tile, subclass `plone.tiles.PersistentTile`
instead. You may also need a schema interface if you want a configurable
transient or persistent tile.

To register the tile, use ZCML like this::

    <configure xmlns:plone="http://namespaces.plone.org/plone">
    
        <plone:tile
            name="sample.tile"
            
            title="A title for the tile"
            description="My tile's description"
            add_permission="my.add.Permission"
            schema=".interfaces.IMyTileSchema" 
            
            class=".mytile.MyTile"
            permission="zope.Public"
            for="*"
            layer="*"
            />
    
    </configure>
    
The first five attributes describe the tile by configuring an appropriate
`ITileType` directive. The rest mimics the `<browser:page />` directive,
so you can specify a `template` file and omit the `class`, or use both a
`template` and `class`.

If you want to register a persistent tile with a custom schema, but a template
only, you can do e.g.::

        <plone:tile
            name="sample.persistenttile"
            title="A title for the tile"
            description="My tile's description"
            add_permission="my.add.Permission"
            schema=".interfaces.IMyTileSchema" 
            class="plone.tiles.PersistentTile"
            template="mytile.pt"
            permission="zope.Public"
            for="*"
            />

If you want to override an existing tile, e.g. with a new layer or more
specific context, you *must* omit the tile metadata (title, description, add
permission or schema). If you include any metadata you will get a conflict
error on Zope startup. This example shows how to use a different template
for our tile::

        <plone:tile
            name="sample.persistenttile"
            template="override.pt"
            permission="zope.Public"
            for="*"
            layer=".interfaces.IMyLayer"
            />

See `tiles.txt` and `directives.txt` for more details.

.. _plone.app.blocks: http://pypi.python.org/pypi/plone.app.blocks

