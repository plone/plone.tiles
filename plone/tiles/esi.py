import re

from zope.interface import implements

from plone.tiles.interfaces import IESIRendered, ESI_HEADER, ESI_HEADER_KEY
from plone.tiles.tile import Tile, PersistentTile

HEAD_CHILDREN = re.compile(r'<head[^>]*>(.*)</head>', re.I | re.S)
BODY_CHILDREN = re.compile(r'<body[^>]*>(.*)</body>', re.I | re.S)

ESI_NAMESPACE_MAP = {'esi': 'http://www.edge-delivery.org/esi/1.0'}
ESI_TEMPLATE = u"""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <body>
        <a class="_esi_placeholder" rel="esi" href="%(url)s/@@%(esiMode)s?%(queryString)s"></a>
    </body>
</html>
"""

def substituteESILinks(rendered):
    """Turn ESI links like <a class="_esi_placeholder" rel="esi" href="..." />
    into <esi:include /> links.

    ``rendered`` should be an HTML string.
    """

    rendered = re.sub(r'<html',
                      '<html xmlns:esi="%s"' % ESI_NAMESPACE_MAP['esi'],
                      rendered, 1)
    return re.sub(r'<a class="_esi_placeholder" rel="esi" href="([^"]+)"></a>',
                  r'<esi:include src="\1" />', rendered)


class ConditionalESIRendering(object):
    head = False
    
    def render(self):
        raise NotImplemented(u"Override render() or set a class variable 'index' to point to a view page template file")
    
    def __call__(self, *args, **kwargs):
        if self.request.getHeader(ESI_HEADER, 'false').lower() == 'true':
            mode = 'esi-body'
            if self.head:
                mode = 'esi-head'
            return ESI_TEMPLATE % {
                    'url': self.request.getURL(),
                    'queryString': self.request.get('QUERY_STRING', ''),
                    'esiMode': mode,
                }
        if hasattr(self, 'index'):
            return self.index(*args, **kwargs)
        
        return self.render()

# Convenience base classes

class ESITile(ConditionalESIRendering, Tile):
    """Convenience class for tiles using ESI rendering.
    
    Set ``head`` to True if this tile renders <head /> content. The
    default is to render <body /> content.
    """
    
    implements(IESIRendered)
    head = False

class ESIPersistentTile(ConditionalESIRendering, PersistentTile):
    """Convenience class for tiles using ESI rendering.
    
    Set ``head`` to True if this tile renders <head /> content. The
    default is to render <body /> content.
    """
    
    implements(IESIRendered)
    head = False

# ESI views

class ESIHead(object):
    """Render the head portion of a tile independently.
    """
    
    def __init__(self, context, request):
        self.tile = context
        self.request = request
    
    def __call__(self):
        """Return the children of the <head> tag as a fragment.
        """
        
        if self.request.getHeader(ESI_HEADER):
            del self.request.environ[ESI_HEADER_KEY]
        
        document = self.tile() # render the tile
        
        match = HEAD_CHILDREN.search(document)
        if not match:
            return document
        return match.group(1).strip()

class ESIBody(object):
    """Render the head portion of a tile independently.
    """
    
    def __init__(self, context, request):
        self.tile = context
        self.request = request
    
    def __call__(self):
        """Return the children of the <head> tag as a fragment.
        """
        
        if self.request.getHeader(ESI_HEADER):
            del self.request.environ[ESI_HEADER_KEY]
        
        document = self.tile() # render the tile
        
        match = BODY_CHILDREN.search(document)
        if not match:
            return document
        return match.group(1).strip()
