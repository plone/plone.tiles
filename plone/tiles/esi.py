import re
from thread import allocate_lock

from zope.interface import implements
from plone.tiles.interfaces import IESIRendered
from plone.tiles.tile import Tile, PersistentTile

HEAD_RE_LOCK = allocate_lock()
HEAD_CHILDREN = re.compile(r'<head[^>]*>(.*)</head>', re.I | re.S)

BODY_RE_LOCK = allocate_lock()
BODY_CHILDREN = re.compile(r'<body[^>]*>(.*)</body>', re.I | re.S)

# Convenience base classes

class ESITile(Tile):
    """Convenience class for tiles using ESI rendering
    """
    
    implements(IESIRendered)

class ESIPersistentTile(PersistentTile):
    """Convenience class for tiles using ESI rendering
    """
    
    implements(IESIRendered)

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
        document = self.tile() # render the tile
        HEAD_RE_LOCK.acquire()
        try:
            match = HEAD_CHILDREN.search(document)
            if not match:
                return document
            return match.group(1).strip()
        finally:
            HEAD_RE_LOCK.release()

class ESIBody(object):
    """Render the head portion of a tile independently.
    """
    
    def __init__(self, context, request):
        self.tile = context
        self.request = request
    
    def __call__(self):
        """Return the children of the <head> tag as a fragment.
        """
        document = self.tile() # render the tile
        BODY_RE_LOCK.acquire()
        try:
            match = BODY_CHILDREN.search(document)
            if not match:
                return document
            return match.group(1).strip()
        finally:
            BODY_RE_LOCK.release()

