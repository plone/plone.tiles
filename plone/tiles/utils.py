import urllib
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import ISequence

from zope import schema

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