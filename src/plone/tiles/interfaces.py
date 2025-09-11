from zope.interface import Interface
from zope.interface.common.mapping import IMapping
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IBrowserView

import zope.schema


ESI_HEADER = "X-ESI-Enabled"
ESI_HEADER_KEY = "HTTP_" + ESI_HEADER.replace("-", "_").upper()


class ITileType(Interface):
    """A utility that describes a type of tile"""

    __name__ = zope.schema.DottedName(title="Tile name (same as utility name)")

    title = zope.schema.TextLine(title="Title")

    description = zope.schema.Text(title="Description", required=False)

    icon = zope.schema.Text(title="Icon", required=False)

    add_permission = zope.schema.Id(title="Zope 3 IPermission utility name")

    schema = zope.schema.Object(
        title="Tile schema",
        description="Describes configurable data for this tile and allows a "
        "form to be rendered to edit it. Set to None if the tile "
        "has no configurable schema",
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
        title="The name of the type of this tile",
        description="This should be a dotted name prefixed with the "
        "package that defined the tile",
    )

    id = zope.schema.DottedName(
        title="Tile instance id",
        description="The id is normally set using sub-path traversal"
        "A given tile type may be used multiple times on "
        "the same page, each with a unique id. The id must "
        "be unique even across multiple layouts for the "
        "same context.",
    )


class ITile(IBasicTile):
    """A tile with some data (probably from a query string)."""

    data = zope.schema.Dict(
        title="The tile's configuration data",
        description="This attribute cannot be set, but the dictionary may "
        "be updated",
        key_type=zope.schema.Id(title="The data element name"),
        value_type=zope.schema.Field(title="The value"),
        required=True,
        readonly=True,
        default={},
    )

    url = zope.schema.URI(
        title="Tile URL",
        description="This is the canonical URL for the tile. In the "
        "case of transient tiles with data, this may "
        "include a query string with parameters. Provided "
        "that the `id` attribute is set, it will also "
        "include a sub-path with this in it.",
    )


class IPersistentTile(ITile):
    """A tile with full-blown persistent data (stored in annotations)."""


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
        """Persist the given data dict."""

    def delete():
        """Delete the data record for this tile."""


class ITileDataContext(Interface):
    """Indirection to help determine where persistent tiles store their data.

    This is a multi-adapter on ``(context, request, tile)``. The context and
    request are the same as ``tile.context`` and ``tile.request``, but these
    discriminators allow the data context to be customised depending on
    the context or request.

    The default implementation simply returns ``tile.context``. That must
    be annotatable for the default tile data storage adapter and
    persistent tile ``ITileDataManager`` to work.
    """


class ITileDataStorage(IMapping):
    """Indirection to help determine how persistent tiles store their data.

    This is a multi-adapter on ``(context, request, tile)``. The context and
    request are the same as ``tile.context`` and ``tile.request``, but these
    discriminators allow the data context to be customised depending on
    the context or request.

    The default implementation simply returns the configured zope.annotation
    storage for the given context.

    The adapter is expected to provide IMapping interface and be accessed
    by tile data managers similarly to zope.annotation storage.
    """


class IFieldTypeConverter(Interface):
    """Field type converter for querystring parameters for Zope."""

    token = zope.schema.TextLine(
        title="Token",
        description="""
                                 String parameter appended to the field id
                                 for the Zope Publisher to cast it.
                                 """,
    )
