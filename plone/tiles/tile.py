import logging

from zope.interface import implements
from zope.component import getMultiAdapter, queryUtility

from zope.publisher.browser import BrowserView

from plone.tiles.interfaces import ITile, IPersistentTile
from plone.tiles.interfaces import ITileType, ITileDataManager

from plone.tiles.data import decode

LOGGER = logging.getLogger('plone.tiles')

class Tile(BrowserView):
    """Basic implementation of a transient tile. Subclasses should override
    __call__ or set an 'index' variable to point to a view page template file.
    """
    
    implements(ITile)
    
    __name__ = None
    __type_name__ = None
    
    __cached_data = None
    
    def __call__(self, *args, **kwargs):
        if not hasattr(self, 'index'):
            raise NotImplemented(u"Override __call__ or set a class variable 'index' to point to a view page template file")
        return self.index(*args, **kwargs)
    
    @property
    def data(self):
        if self.__cached_data is None:
            tile_type = queryUtility(ITileType, name=self.__type_name__)
            if tile_type is None or tile_type.schema is None:
                self.__cached_data = {}
            else:
                try:
                    self.__cached_data = decode(self.request.form, tile_type.schema, missing=True)
                except (ValueError, UnicodeDecodeError,):
                    LOGGER.exception(u"Could not convert form data to schema")
                    self.__cached_data = self.request.form
        return self.__cached_data

class PersistentTile(Tile):
    """Base class for persistent tiles. Identical to `Tile`, except that the
    data dict is never serialized with the URL.
    """
    
    implements(IPersistentTile)
    
    __cached_data = None
    
    @property
    def data(self):
        if self.__cached_data is None:
            reader = getMultiAdapter((self.context, self,), ITileDataManager)
            self.__cached_data = reader.get()
        return self.__cached_data
