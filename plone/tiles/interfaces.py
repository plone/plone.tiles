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
    
    It will normally be traversed to like this::
    
        http://localhost:8080/plone-site/object/@@my.tile?id=tile1
    
    In this case:
    
    * The tile context is the content object at /plone-site/object.
    * The `__name__` is 'my.tile'
    * The `id` is `tile1`
    """
    
    __name__ = zope.schema.DottedName(
            title=u"The name of the type of this tile",
            description=u"This should be a dotted name prefixed with the "
                         "package that defined the tile",
        )
    
    id = zope.schema.DottedName(
            title=u"Tile instance id",
            description=u"The id is normally set using a query string"
                          "parameter `id`. A given tile type may be used "
                          "multiple times on the same page, each with a "
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
    
    This is an adapter on (context, tile). The tile's id must be set.
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
