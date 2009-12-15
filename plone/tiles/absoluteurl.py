import urllib

from zope.component import getMultiAdapter
from zope.component import queryUtility

from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL

from plone.tiles.interfaces import ITileType, ITileDataManager
from plone.tiles.data import encode

_safe = '@+'

class BaseTileAbsoluteURL(AbsoluteURL):
    """Convenience base class
    """
    
    def __str__(self):
        tile = self.context
        request = self.request

        id = tile.id
        name = tile.__name__
        context = tile.__parent__
        
        if id is None or name is None or context is None:
            raise TypeError("Insufficient context to determine URL")
        
        url = str(getMultiAdapter((context, request), IAbsoluteURL))
        
        if name:
            url += '/@@%s?id=%s' % (urllib.quote(name.encode('utf-8'), _safe), 
                                    urllib.quote(id.encode('utf-8'), _safe),)

        return url

    def breadcrumbs(self):
        tile = self.context
        request = self.request
        
        id = tile.id
        name = tile.__name__
        context = tile.__parent__

        base = tuple(getMultiAdapter((context, request), IAbsoluteURL).breadcrumbs())        
        base += ({'name': name,
                  'url': "%s/@@%s?id=%s" % (base[-1]['url'],
                                            urllib.quote(name.encode('utf-8'), _safe), 
                                            urllib.quote(id.encode('utf-8'), _safe),),
                  },)
        
        return base

class TransientTileAbsoluteURL(BaseTileAbsoluteURL):
    """Absolute URL for a transient tile. Includes the tile traverser and
    tile data encoded in the query string.
    """
    
    def __str__(self):
        url = super(TransientTileAbsoluteURL, self).__str__()
        data = ITileDataManager(self.context).get()
        if data:
            tileType = queryUtility(ITileType, name=self.context.__name__)
            if tileType is not None and tileType.schema is not None:
                url += '&' + encode(data, tileType.schema)
        return url

class PersistentTileAbsoluteURL(BaseTileAbsoluteURL):
    """Absolute URL for a persitent tile. Includes the tile traverser, but no
    tile data encoded in the query string.
    """
