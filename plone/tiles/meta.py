from zope.interface import Interface

from zope import schema
from zope.configuration.fields import (
    GlobalObject, GlobalInterface, MessageID, Path)
from zope.security.zcml import Permission

from zope.configuration.exceptions import ConfigurationError

from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.tiles.interfaces import ITileType
from plone.tiles.type import TileType
from plone.tiles.tile import Tile

from zope.component.zcml import utility

try:
    from Products.Five.browser.metaconfigure import page
except ImportError:
    from zope.app.publisher.browser.viewmeta import page

class ITileDirective(Interface):
    """Directive which registers a new type of tile
    """
    
    name = schema.DottedName(
            title=u"Name",
            description=u"A unique, dotted name for the tile",
        )
    
    title = MessageID(
            title=u"Title",
            description=u"A user friendly title, used when configuring the tile",
            required=False
        )

    description = MessageID(
            title=u"Description",
            description=u"A longer summary of the tile's purpose and function",
            required=False
        )
        
    add_permission = Permission(
            title=u"Add permission",
            description=u"Name of the permission required to instantiate this tile",
            required=False,
        )
    
    schema = GlobalInterface(
            title=u"Configuration schema for the tile",
            description=u"This is used to create standard add/edit forms",
            required=False,
        )
    
    for_ = GlobalObject(
            title=u"The interface or class this tile is available for",
            required=False,
        )
    
    layer = GlobalInterface(
            title=u"The layer the tile is available for",
            required=False
        )

    class_ = GlobalObject(
            title=u"Class",
            description=u"Class implementing this tile",
            required=False
        )

    template = Path(
            title=u"The name of a template that renders this tile",
            description=u"Refers to a file containing a page template",
            required=False,
        )
        
    permission = Permission(
            title=u"View permission",
            description=u"Name of the permission required to view this item",
            required=False,
        )

def tile(_context, name,
            title=None, description=None, add_permission=None, schema=None,
            for_=None, layer=None, class_=None, template=None, permission=None):
    """Implements the <plone:tile /> directive
    """
    
    if title is not None or description is not None or add_permission is not None or schema is not None:
        if title is None or add_permission is None:
            raise ConfigurationError(u"When configuring a new type of tile, 'title' and 'add_permission' are required")
    
        type_ = TileType(name, title, add_permission, description, schema)
        
        utility(_context, provides=ITileType, component=type_, name=name)
    
    if for_ is not None or layer is not None or class_ is not None or template is not None or permission is not None:
        if class_ is None and template is None:
            raise ConfigurationError(u"When configuring a tile, 'class' or 'template' must be given.")
        if permission is None:
            raise ConfigurationError(u"When configuring a tile, 'permission' is required")
        
        if for_ is None:
            for_ = Interface
        if layer is None:
            layer = IDefaultBrowserLayer
        
        if class_ is None:
            class_ = Tile
            
        page(_context, name=name, permission=permission, for_=for_, layer=layer,
                template=template, class_=class_)
