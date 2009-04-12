import urllib

from zope.interface import implements
from zope.component import adapts, queryUtility

from zope.schema import getFieldsInOrder, getFields
from zope.schema.interfaces import ISequence

from zope import schema

from zope.annotation.interfaces import IAnnotatable, IAnnotations

from plone.tiles.interfaces import ITileType
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
    
    def __init__(self, context, tile):
        self.context = context
        self.tile = tile
        
        self.tile_type = queryUtility(ITileType, name=tile.__type_name__)
        
        self.annotations = IAnnotations(context)
        self.key = "%s.%s" % (ANNOTATIONS_KEY_PREFIX, tile.__name__,)
        
    def get(self):
        """Get the data 
        """
        data = dict(self.annotations.get(self.key, {}))
        if self.tile_type is not None and self.tile_type.schema is not None:
            for name, field in getFields(self.tile_type.schema).items():
                if name not in data:
                    data[name] = field.missing_value
        return data

    def set(self, data):
        """Set the data
        """
        self.annotations[self.key] = PersistentDict(data)
    
    def delete(self):
        """Delete the data
        """
        if self.key in self.annotations:
            del self.annotations[self.key]

# Encoding

# Types not in this dict or explicitly set to None are not supported and will
# result in a ValueError.

type_to_converter = {
    
    # Strings - not type converted

    schema.BytesLine        : '',
    schema.ASCIILine        : '',
    schema.TextLine         : '',
    
    schema.URI              : '',
    schema.Id               : '',
    schema.DottedName       : '',
    
    # Choice - assumes the value of the vocabulary is a string!
    
    schema.Choice           : '',
    
    # Text types - may allow newlines
    
    schema.Bytes            : 'text',
    schema.Text             : 'text',
    schema.ASCII            : 'text',

    # Numeric types

    schema.Int              : 'long',
    schema.Float            : 'float',

    # Bools - note that False is encoded as ''
    
    schema.Bool             : 'boolean',

    # Sequence types
    
    schema.Tuple            : 'tuple',
    schema.List             : 'list',
    
}

def encode(data, schema, ignore=()):
    """Given a data dictionary with key/value pairs and schema, return an
    encoded query string. This is similar to urllib.urlencode(), but field
    names will include the appropriate field type converters, e.g. an int
    field will be encoded as fieldname:int=123. Fields not found in the data
    dict will be ignored, and items in the dict not in the schema will also
    be ignored. Additional fields to ignore can be passed with the 'ignore'
    parameter. If any fields cannot be converted, a KeyError will be raised.
    """
    
    encode = []
    
    for name, field in getFieldsInOrder(schema):
        if name in ignore or name not in data:
            continue
        converter = type_to_converter.get(field.__class__, None)
        if converter is None:
            raise KeyError(u"Cannot URL encode %s of type %s" % (name, field.__class__,))
        
        encoded_name = name
        if converter:
            encoded_name = "%s:%s" % (name, converter,)
        
        if ISequence.providedBy(field):
            value_type_converter = type_to_converter.get(field.value_type.__class__, None)
            if value_type_converter is None:
                raise KeyError(u"Cannot URL encode value type for %s of type %s : %s" % \
                                (name, field.__class__, field.value_type.__class__,))
            
            if value_type_converter:
                encoded_name = "%s:%s:%s" % (name, value_type_converter, converter,)
        
        value = data[name]
        
        # The :bool converter just does bool() value, but urlencode() does
        # str() on the object. The result is False => 'False' => True :(
        if isinstance(value, bool):
            if value:
                value = '1'
            else:
                value = ''
        
        encode.append((encoded_name, data[name]))
    
    return urllib.urlencode(encode)

# Decoding

def decode(data, schema, missing=True):
    """Decode a data dict according to a schema. The returned dictionary will
    contain only keys matching schema names, and will force type values 
    appropriately.
    
    This function is only necessary because the encoders used by encode()
    are not sufficiently detailed to always return the exact type expected
    by a field, e.g. resulting in ascii/unicode discrepancies.
    
    If missing is True, fields that are in the schema but not the field will
    be set to field.missing_value. Otherwise, they are ignored.
    """
    
    decoded = {}
    
    for name, field in getFields(schema).items():
        if name not in data:
            if missing:
                decoded[name] = field.missing_value
            continue
        
        value = data[name]
        
        field_type = field._type
        if isinstance(field_type, (tuple, list,)):
            field_type = field_type[-1]
        
        if ISequence.providedBy(field):
            converted = []
            
            value_type_field_type = field.value_type._type
            if isinstance(value_type_field_type, (tuple, list,)):
                value_type_field_type = value_type_field_type[-1]
            
            for item in value:
                if not isinstance(item, field.value_type._type):
                    item = value_type_field_type(item)
                converted.append(item)
            
            value = converted
        
        if not isinstance(value, field._type):
            value = field_type(value)

        decoded[name] = value

    return decoded