from zope.interface import implements
from plone.tiles.interfaces import IFieldTypeConverter


class NoConverter(object):
    implements(IFieldTypeConverter)
    
    def __init__(self, field):
        self.field = field

    token = None

class TextConverter(NoConverter):
    token = 'text'

class LongConverter(NoConverter):
    token = 'long'

class FloatConverter(NoConverter):
    token = 'float'

class BoolConverter(NoConverter):
    token = 'boolean'

class TupleConverter(NoConverter):
    token = 'tuple'

class ListConverter(NoConverter):
    token = 'list'
