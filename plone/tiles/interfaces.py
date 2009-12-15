from zope.interface import Interface
import zope.schema

from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IBrowserView

class ITileType(Interface):
    """A utility that describes a type of tile 
    """
    
    __name__ = zope.schema.DottedName(title=u"Tile name (same as utility name)")
    
    title = zope.schema.TextLine(title=u"Title")
    
    description = zope.schema.Text(title=u"Description", required=False)
    
    add_permission = zope.schema.Id(title=u"Zope 3 IPermission utility name")
    
    schema = zope.schema.Object(
            title=u"Tile schema",
            description=u"Describes configurable data for this tile and "
                         "allows a form to be rendered to edit it. Set to "
                         "None if the tile has no configurable schema",
            schema=IInterface,
            required=False,
        )

class IBasicTile(IBrowserView):
    """A tile is a publishable resource that can be inserted into a site or
    page layout.

    The tile should be a named multi adapter on (<context>, <layer>)
    providing IBasicTile.
    
    Ordinarily, the ++tile++ namespace traversal adapter will be used to
    initialise the tile instance. Thus, if a tile is published as:
    
        http://localhost:8080/plone-site/object/++tile++tile1/tile-type
    
    then __type_name__ is set to 'tile-type', __name__ is set to 'tile1'.
    The tile context is the content object at /plone-site/object.
    """
    
    __type_name__ = zope.schema.DottedName(
            title=u"The name of the type of this tile",
            description=u"This should be a dotted name prefixed with the "
                         "package that defined the tile",
        )
    
    __name__ = zope.schema.DottedName(
            title=u"Tile instance name",
            description=u"The name is set upon traversal. A given tile type "
                          "may be instantiated multiple times, each with a "
                          "unique id. The id must be unique even across "
                          "multiple layouts for the same context. "
        )
    
    
    
class ITile(IBasicTile):
    """A tile with some data (probably from a query string).
    """
        
    data = zope.schema.Dict(
            title=u"The tile's configuration data",
            description=u"This attribute cannot be set, but the dictionary may be updated",
            key_type=zope.schema.Id(title=u"The data element name"),
            value_type=zope.schema.Field(title=u"The value"),
            required=True,
            readonly=True,
            default={},
        )

class IPersistentTile(ITile):
    """A tile with full-blown persistent data (stored in annotations).
    """

class ITileDataManager(Interface):
    """Support for getting and setting tile data dicts.
    
    This is an adapter on (context, tile). The tile's __name__ must be set.
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

class ITileAddView(IBrowserView):
    """A tile add view as found by the ++addtile++ traverser.
    
    The default add view is an adapter from (context, request, tile_info) to
    this interface. Per-tile type overrides can be created by registering
    named adapters matching the tile name.
    """
