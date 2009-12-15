from zope.interface import implements

from zope.publisher.browser import BrowserView

from plone.tiles.interfaces import ITile, IPersistentTile
from plone.tiles.interfaces import ITileDataManager

class Tile(BrowserView):
    """Basic implementation of a transient tile. Subclasses should override
    __call__ or set an 'index' variable to point to a view page template file.
    """
    
    implements(ITile)
    
    __name__ = None
    id = None
    
    __cachedData = None
    
    def __init__(self, context, request):
        super(Tile, self).__init__(context, request)
        if request is not None:
            self.id = request.form.get('id', None)
    
    def __call__(self, *args, **kwargs):
        if not hasattr(self, 'index'):
            raise NotImplemented(u"Override __call__ or set a class variable 'index' to point to a view page template file")
        return self.index(*args, **kwargs)
    
    @property
    def data(self):
        if self.__cachedData is None:
            reader = ITileDataManager(self)
            self.__cachedData = reader.get()
        return self.__cachedData

class PersistentTile(Tile):
    """Base class for persistent tiles. Identical to `Tile`, except that the
    data dict is never serialized with the URL.
    """
    
    implements(IPersistentTile)
