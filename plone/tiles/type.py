from zope.interface import implements
from plone.tiles.interfaces import ITileType

class TileType(object):
    """A utility that describes a type of tile 
    """
    
    implements(ITileType)
    
    def __init__(self, name, title, add_permission, description=None, schema=None):
        self.__name__ = name
        self.title = title
        self.add_permission = add_permission
        self.description = description
        self.schema = schema
    
    def __repr__(self):
        return u"<TileType %s (%s)>" % (self.__name__, self.title,)