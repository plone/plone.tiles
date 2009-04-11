from zope.interface import implements
from zope.component import adapts

from zope.annotation.interfaces import IAnnotatable, IAnnotations

from plone.tiles.interfaces import IPersistentTile
from plone.tiles.interfaces import ITileDataManager

from persistent.dict import PersistentDict

ANNOTATIONS_KEY_PREFIX = u'plone.tiles.data'

class AnnotationsTileDataManager(object):
    """A data reader for persistent tiles operating on annotatable contexts.
    The data is retrieved from an annotation.
    """
    
    implements(ITileDataManager)
    adapts(IAnnotatable, IPersistentTile)
    
    def __init__(self, context, request, tile):
        self.context = context
        self.request = request
        self.tile = tile
        
        self.annotations = IAnnotations(context)
        self.key = "%s.%s" % (ANNOTATIONS_KEY_PREFIX, tile.__name__,)
        
    def get(self):
        """Get the data 
        """
        return dict(self.annotations.get(self.key, {}))

    def set(self, data):
        """Set the data
        """
        self.annotations[self.key] = PersistentDict(data)
    
    def delete(self):
        """Delete the data
        """
        if self.key in self.annotations:
            del self.annotations[self.key]
