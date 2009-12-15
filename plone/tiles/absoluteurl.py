import urllib

from zope.component import getMultiAdapter
from zope.component import queryUtility

from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL

from plone.tiles.interfaces import ITileType
from plone.tiles.data import encode

_safe = '@+'

class BaseTileAbsoluteURL(AbsoluteURL):
    """Convenience base class
    """
    
    def __str__(self):
        tile = self.context
        request = self.request

        name = tile.__name__
        typeName = tile.__type_name__
        context = tile.__parent__
        
        if name is None or typeName is None or context is None:
            raise TypeError("Insufficient context to determine URL")
        
        url = str(getMultiAdapter((context, request), IAbsoluteURL))
        
        if name:
            url += '/++tile++%s/%s' % (urllib.quote(name.encode('utf-8'), _safe), 
                                       urllib.quote(typeName.encode('utf-8'), _safe),)

        return url

    def breadcrumbs(self):
        tile = self.context
        request = self.request
        
        name = tile.__name__
        typeName = tile.__type_name__
        context = tile.__parent__

        base = tuple(getMultiAdapter((context, request), IAbsoluteURL).breadcrumbs())        
        base += ({'name': name,
                  'url': "%s/++tile++%s/%s" % (base[-1]['url'],
                                               urllib.quote(name.encode('utf-8'), _safe), 
                                               urllib.quote(typeName.encode('utf-8'), _safe),),
                  },)
        
        return base

class TileAbsoluteURL(BaseTileAbsoluteURL):
    """Absolute URL for a transient tile. Includes the tile traverser and
    tile data encoded in the query string.
    """
    
    def __str__(self):
        url = super(TileAbsoluteURL, self).__str__()
        data = self.context.data
        if data:
            tileType = queryUtility(ITileType, name=self.context.__type_name__)
            if tileType is not None and tileType.schema is not None:
                url += '?' + encode(data, tileType.schema)
        return url

class PersistentTileAbsoluteURL(BaseTileAbsoluteURL):
    """Absolute URL for a persitent tile. Includes the tile traverser, but no
    tile data encoded in the query string.
    """
