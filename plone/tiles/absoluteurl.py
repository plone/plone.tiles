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
        
        if name is None or context is None:
            raise TypeError("Insufficient context to determine URL")
        
        url = str(getMultiAdapter((context, request), IAbsoluteURL))
        
        tileFragment = "@@" + urllib.quote(name.encode('utf-8'), _safe)
        if id:
            tileFragment += '/' + urllib.quote(id.encode('utf-8'), _safe)
        
        return '%s/%s' % (url, tileFragment,)

    def breadcrumbs(self):
        tile = self.context
        request = self.request
        
        id = tile.id
        name = tile.__name__
        context = tile.__parent__
        
        tileFragment = "@@" + urllib.quote(name.encode('utf-8'), _safe)
        if id:
            tileFragment += '/' + urllib.quote(id.encode('utf-8'), _safe)
        
        base = tuple(getMultiAdapter((context, request), IAbsoluteURL).breadcrumbs())        
        base += ({'name': name,
                  'url': "%s/%s" % (base[-1]['url'], tileFragment,),
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
                if '?' in url:
                    url += '&' + encode(data, tileType.schema)
                else:
                    url += '?' + encode(data, tileType.schema)
        return url

class PersistentTileAbsoluteURL(BaseTileAbsoluteURL):
    """Absolute URL for a persitent tile. Includes the tile traverser, but no
    tile data encoded in the query string.
    """
