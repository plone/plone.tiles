# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IBrowserView

import zope.schema


ESI_HEADER = 'X-ESI-Enabled'
ESI_HEADER_KEY = 'HTTP_' + ESI_HEADER.replace('-', '_').upper()


class ITileType(Interface):
    """A utility that describes a type of tile
    """

    __name__ = zope.schema.DottedName(
        title=u"Tile name (same as utility name)")

    title = zope.schema.TextLine(title=u"Title")

    description = zope.schema.Text(title=u"Description", required=False)

    icon = zope.schema.Text(title=u"Icon", required=False)

    add_permission = zope.schema.Id(title=u"Zope 3 IPermission utility name")

    schema = zope.schema.Object(
        title=u"Tile schema",
        description=u"Describes configurable data for this tile and allows a "
                    u"form to be rendered to edit it. Set to None if the tile "
                    u"has no configurable schema",
        schema=IInterface,
        required=False,
    )


class IBasicTile(IBrowserView):
    """A tile is a publishable resource that can be inserted into a site or
    page layout.

    The tile should be a named multi adapter on (<context>, <layer>)
    providing IBasicTile.

    It will normally be traversed to like this::

        http://localhost:8080/plone-site/object/@@my.tile/tile1

    In this case:

    * The tile context is the content object at /plone-site/object.
    * The ``__name__`` of the tile instance is 'my.tile'
    * The ``id`` of the tile instance is 'tile1'
    * The ``url`` of the tile instance is the URL as above
    """

    __name__ = zope.schema.DottedName(
        title=u"The name of the type of this tile",
        description=u"This should be a dotted name prefixed with the "
                    u"package that defined the tile",
    )

    id = zope.schema.DottedName(
        title=u"Tile instance id",
        description=u"The id is normally set using sub-path traversal"
                    u"A given tile type may be used multiple times on "
                    u"the same page, each with a unique id. The id must "
                    u"be unique even across multiple layouts for the "
                    u"same context."
    )


class ITile(IBasicTile):
    """A tile with some data (probably from a query string).
    """

    data = zope.schema.Dict(
        title=u"The tile's configuration data",
        description=u"This attribute cannot be set, but the dictionary may "
                    u"be updated",
        key_type=zope.schema.Id(title=u"The data element name"),
        value_type=zope.schema.Field(title=u"The value"),
        required=True,
        readonly=True,
        default={},
    )

    url = zope.schema.URI(
        title=u"Tile URL",
        description=u"This is the canonical URL for the tile. In the "
                    u"case of transient tiles with data, this may "
                    u"include a query string with parameters. Provided "
                    u"that the `id` attribute is set, it will also "
                    u"include a sub-path with this in it.",
    )


class IPersistentTile(ITile):
    """A tile with full-blown persistent data (stored in annotations).
    """


class IESIRendered(Interface):
    """Marker interface for tiles which are to be rendered via ESI.

    Two corresponding views, @@esi-body and @@esi-head, will be made available
    on the tile itself. This will return the children of the <head /> or
    <body /> of the tile, respectively.

    Thus, a tile marked with this interface may be replaced with an ESI
    instruction like::

        <esi:include src="./@@my.tile/tile-id/@@esi-body" />

    When fetched, this placeholder will be replaced by the body of the tile.
    """


class ITileDataManager(Interface):
    """Support for getting and setting tile data dicts.

    This is an adapter on a tile. The tile's id must be set.
    """

    def get():
        """Get a dictionary with tile data for this tile. The dictionary is
        disconnected from the underlying storage.
        """

    def set(data):
        """Persist the given data dict.
        """

    def delete():
        """Delete the data record for this tile.
        """


class ITileDataContext(Interface):
    """Indirection to help determine where persistent tiles store their data.

    This is a multi-adapter on ``(context, request, tile)``. The context and
    request are the same as ``tile.context`` and ``tile.request``, but these
    discriminators allow the data context to be customised depending on
    the context or request.

    The default implementation simply returns ``tile.context``. That must
    be annotatable for the default persistent tile ``ITileDataManager``
    to work.
    """


class IFieldTypeConverter(Interface):
    """Field type converter for querystring parameters for Zope."""

    token = zope.schema.TextLine(title=u"Token",
                                 description=u"""
                                 String parameter appended to the field id
                                 for the Zope Publisher to cast it.
                                 """)
