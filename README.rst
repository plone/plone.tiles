plone.tiles
===========

.. image:: https://secure.travis-ci.org/plone/plone.tiles.png
   :target: http://travis-ci.org/plone/plone.tiles

``plone.tiles`` implements a low-level, non-Plone/Zope2-specific support for creating "tiles".

.. contents::


Introduction
------------

For the purposes of this package,
a tile is a browser view and an associated utility providing some metadata about that view.
The metadata includes a title and description,
an 'add' permission and optionally a schema interface describing configurable aspects of the tile.
The idea is that a UI (such as Deco) can present the user with a list of insertable tiles and optionally render a form to configure the tile upon insertion.

A tile is inserted into a layout as a link:

.. code:: xml

    <link rel="tile" target="placeholder" href="./@@sample.tile/tile1?option1=value1" />

The sub-path (``tile1`` in this case) is used to set the tile ``id`` attribute.
This allows the tile to know its unique id, and, in the case of persistent tiles, look up its data.
``sample.tile`` is the name of the browser view that implements the tile.
This is made available as the ``__name__`` attribute.
Other parameters may be turned into tile data, available under the ``data`` attribute, a dict, for regular tiles.
For persistent tiles
(those deriving from the ``PersistentTile`` base class),
the data is fetched from annotations instead,
based on the tile id.

There are three interfaces describing tiles in this package:

``IBasicTile``
    is the low-level interface for tiles.
    It extends ``IBrowserView`` to describe the semantics of the ``__name__`` and  ``id`` attributes.
``ITile``
    describes a tile that can be configured with some data.
    The data is accessible via a dict called ``data``.
    The default implementation of this interface, ``plone.tiles.Tile``,
    will use the schema of the tile type and the query string (``self.request.form``) to construct that dictionary.
    This interface also describes an attribute ``url``,
    which gives the canonical tile URL,
    including the id sub-path and any query string parameters.
    (Note that tiles also correctly implement ``IAbsoluteURL``.)
```IPersistentTile``
    describes a tile that stores its configuration in object annotations,
    and is needed when configuration values cannot be encoded into a query string.
    The default implementation is in ``plone.tiles.PersistentTile``.
    To make it possible to have several tiles of a given type on the same layout,
    the annotations are keyed by the tile ``__name__``.

Internally tiles are described by ``ITileType``.
It contains attributes for the tile name, title, description, add permission and schema (if required).

A properly configured tile consists of

- a utility providing ``ITileType`` with the same name as the tile browser view.
- a browser view providing ``IBasicTile`` or one of its derivatives.

The directive ``<plone:tile ... />`` is used to register both of these components in one go.

To support creation of appropriate tile links, ``plone.tiles.data`` contains two methods:

1) ``encode()`` and
2) ``decode()``

to help turn a data dictionary into a query string and turn a `request.form` dict into a data dict that complies with a tile's schema interface.


Creating a Simple Tile
----------------------

The most basic tile looks like this:

.. code:: python

    from plone.tiles import Tile

    class MyTile(Tile):

        def __call__(self):
            return u"<html><body><p>Hello world</p></body></html>"

Note that the tile is expected to return a complete HTML document.
This will be interpolated into the page output according to the following rules:

* The contents of the tile's ``<head />`` section is appended to the output document's ``<head />`` section.
* The contents of the tile's ``<body />`` section will replace the tile placeholder as indicated by the tile link.

Note that this package does *not* provide these interpolations.
For a Plone implementation of the interpolation algorithm, see `plone.app.blocks`_

If you require a persistent tile, subclass ``plone.tiles.PersistentTile`` instead.
You may also need a schema interface if you want a configurable transient or persistent tile.

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

The first five attributes describe the tile by configuring an appropriate ``ITileType`` directive.
The rest mimics the ``<browser:page />`` directive, so you can specify a ``template`` file and omit the ``class``, or use both a ``template`` and ``class``.

If you want to register a persistent tile with a custom schema, but a template only, you can do e.g.::

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

If you want to override an existing tile, e.g. with a new layer or more specific context,
you *must* omit the tile metadata (title, description, icon, add permission or schema).
If you include any metadata you will get a conflict error on Zope startup. This example shows how to use a different template for our tile::

        <plone:tile
            name="sample.persistenttile"
            template="override.pt"
            permission="zope.Public"
            for="*"
            layer=".interfaces.IMyLayer"
            />

ZCML Reference
--------------

The ``plone:tile`` directive uses the namespace ``xmlns:plone="http://namespaces.plone.org/plone"``.
In order to enable it loading of its ``meta.zcml`` is needed, use::

    <include package="plone.tiles" file="meta.zcml" />

When registering a tile, in the background two registrations are done:

1) How to **add** the tile (registered as a utility component as a instance of ``plone.tiles.type.TileType``).

   It is possible to register a tile without adding capabilities.
   However, such a tile needs to be directly called, there wont be any TTW adding possible.

   This registration can be done once only.

   This registration uses the following attributes:

   - ``name`` (required)
   - ``title`` (required)
   - ``description`` (optional)
   - ``icon`` (optional)
   - ``permission`` (required)
   - ``add_permission`` (required for adding capabilities)
   - ``edit_permission`` (optional, default to add_permission)
   - ``delete_permission`` (optional, default to add_permission)
   - ``schema`` (optional)

2) How to **render** the tile (as a usal page).

   It is possible to register different renderers for the same ``name`` but for different contexts (``for`` or ``layer``).

   This registration uses the following attributes:

   - ``name`` (required)
   - ``for`` (optional)
   - ``layer`` (optional)
   - ``class`` (this or ``template`` or both is required)
   - ``template`` (this or ``class`` or both is required)
   - ``permission`` (required)

The **directives attributes** have the following meaning:

``name``
    A unique, dotted name for the tile.

``title``
    A user friendly title, used when configuring the tile.

``description``
    A longer summary of the tile's purpose and function.

``icon``
    Image that represents tile purpose and function.

``permission``
    Name of the permission required to view the tile.

``add_permission``
    Name of the permission required to instantiate the tile.

``edit_permission``
    Name of the permission required to modify the tile.
    Defaults to the ``add_permission``.

``delete_permission``
    Name of the permission required to remove the tile.
    Defaults to the ``add_permission``.

``schema``
    Configuration schema for the tile.
    This is used to create standard add/edit forms.

``for``
    The interface or class this tile is available for.

``layer``
    The layer (request marker interface) the tile is available for.

``class``
    Class implementing this tile. A browser view providing ``IBasicTile`` or one of its derivates.

``template``
    The name of a template that renders this tile.
    Refers to a file containing a page template.


Further Reading
---------------

See `tiles.rst` and `directives.rst` for more details.

.. _plone.app.blocks: http://pypi.python.org/pypi/plone.app.blocks

