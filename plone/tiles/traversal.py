from zope.interface import implements, Interface
from zope.component import adapts, queryMultiAdapter, queryUtility

from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError

from zope.publisher.interfaces.browser import IBrowserRequest

from plone.tiles.interfaces import IBasicTile, ITileType, ITileAddView

class TileTraverser(object):
    """Implements the ++tile++ namespace.
    
    Traversing to /path/to/obj/++tile++tile-id/tile-name will:
    
      * Look up the tile as a named multi-adapter with name 'tile-name', 
        providing IBasicTile and adapting 'obj' and the request
      * Set the tile's __type_name__ to be 'tile-name'
      * Set the tile's __name__ to be 'tile-id'
      * Return the tile.
    """
    
    implements(ITraversable)
    adapts(Interface, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def traverse(self, name, further):
        
        if len(further) == 0:
            raise TraversalError(self.context, name)
        
        view_name = further.pop(0)
        
        if view_name and view_name.startswith('@@'):
            view_name = view_name[2:]
        
        tile = queryMultiAdapter((self.context, self.request), IBasicTile, name=view_name)
        
        if tile is None:
            raise TraversalError(self.context, name)
        
        tile.__name__ = name
        tile.__type_name__ = view_name
        tile.__parent__ = self.context
        
        return tile

class TileAddViewTraverser(object):
    """Implements the ++addtile++ namespace.
    
    Traversing to /path/to/obj/++addtile++tile-name will:
    
        * Look up the tile info for 'tile-name' as a named utility
        * Attempt to find an adapter for (context, request, tile_info) with
            the name 'tile-name'
        * Fall back on the unnamed adapter of the same triple
        * Return the view for rendering
    """

    implements(ITraversable)
    adapts(Interface, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, further):
        
        tile_info = queryUtility(ITileType, name=name)
        if tile_info is None:
            raise TraversalError(self.context, name)
        
        view = queryMultiAdapter((self.context, self.request, tile_info), ITileAddView, name=name)
        if view is None:
            view = queryMultiAdapter((self.context, self.request, tile_info), ITileAddView)
        
        if view is None:
            raise TraversalError(self.context, name)
        
        view.__name__ = name
        view.__parent__ = self.context
        
        return view
