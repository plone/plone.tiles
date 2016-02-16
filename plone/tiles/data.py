# -*- coding: utf-8 -*-
from persistent.dict import PersistentDict
from plone.tiles.interfaces import IFieldTypeConverter
from plone.tiles.interfaces import IPersistentTile
from plone.tiles.interfaces import ITile
from plone.tiles.interfaces import ITileDataContext
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import ISequence

import json
import logging
import urllib


ANNOTATIONS_KEY_PREFIX = u'plone.tiles.data'
LOGGER = logging.getLogger('plone.tiles')


@adapter(ITile)
@implementer(ITileDataManager)
def transientTileDataManagerFactory(tile):
    if tile.request.get('X-Tile-Persistent'):
        return PersistentTileDataManager(tile)
    else:
        return TransientTileDataManager(tile)


@adapter(ITile)
@implementer(ITileDataManager)
class TransientTileDataManager(object):
    """A data manager for transient tile data, which reads data from the
    request query string.
    """

    def __init__(self, tile):
        self.tile = tile
        self.tileType = queryUtility(ITileType, name=tile.__name__)
        self.annotations = IAnnotations(
            self.tile.request,
            self.tile.request.form
        )
        self.key = '.'.join([ANNOTATIONS_KEY_PREFIX, str(tile.id)])

    def get(self):
        # use explicitly set data (saved as annotation on the request)
        if self.key in self.annotations:
            data = dict(self.annotations[self.key])

            if self.tileType is not None and self.tileType.schema is not None:
                for name, field in getFields(self.tileType.schema).items():
                    if name not in data:
                        data[name] = field.missing_value

        # try to use a '_tiledata' parameter in the request
        elif '_tiledata' in self.tile.request.form:
            data = json.loads(self.tile.request.form['_tiledata'])

        # fall back to the copy of request.form object itself
        else:
            # If we don't have a schema, just take the request
            if self.tileType is None or self.tileType.schema is None:
                data = self.tile.request.form.copy()
            else:
                # Try to decode the form data properly if we can
                try:
                    data = decode(self.tile.request.form,
                                  self.tileType.schema, missing=True)
                except (ValueError, UnicodeDecodeError,):
                    LOGGER.exception(u'Could not convert form data to schema')
                    return self.data.copy()

        return data

    def set(self, data):
        self.annotations[self.key] = data

    def delete(self):
        if self.key in self.annotations:
            self.annotations[self.key] = {}


@adapter(IPersistentTile)
@implementer(ITileDataManager)
class PersistentTileDataManager(object):
    """A data reader for persistent tiles operating on annotatable contexts.
    The data is retrieved from an annotation.
    """

    def __init__(self, tile):
        self.tile = tile
        self.tileType = queryUtility(ITileType, name=tile.__name__)

        self.context = getMultiAdapter(
            (tile.context, tile.request, tile), ITileDataContext)
        self.annotations = IAnnotations(self.context)

        self.key = '.'.join([ANNOTATIONS_KEY_PREFIX, str(tile.id)])

    def _get_default_request_data(self):
        # If we don't have a schema, just take the request
        if self.tileType is None or self.tileType.schema is None:
            data = self.tile.request.form.copy()
        else:
            # Try to decode the form data properly if we can
            try:
                data = decode(self.tile.request.form,
                              self.tileType.schema, missing=True)
            except (ValueError, UnicodeDecodeError,):
                LOGGER.exception(u'Could not convert form data to schema')
                return self.data.copy()
        return data

    def get(self):
        data = self._get_default_request_data()
        data.update(dict(self.annotations.get(self.key, {})))
        if self.tileType is not None and self.tileType.schema is not None:
            for name, field in getFields(self.tileType.schema).items():
                if name not in data:
                    data[name] = field.missing_value
        return data

    def set(self, data):
        self.annotations[self.key] = PersistentDict(data)

    def delete(self):
        if self.key in self.annotations:
            del self.annotations[self.key]


@implementer(ITileDataContext)
@adapter(Interface, Interface, ITile)
def defaultTileDataContext(context, request, tile):
    return tile.context

# Encoding


def map_to_pairs(encoded_name, value):
    """Given an encoded basename, e.g. "foo:record" or "foo:record:list" and
    a dictionary value, yields (encoded_name, value) pairs to be included
    in the final encode.
    """
    prefix, postfix = encoded_name.split(':', 1)
    postfix = postfix.replace('record:list', 'records')

    def guess_type(v):
        if isinstance(v, str):
            return ''
        if isinstance(v, bool):
            return ':boolean'
        if isinstance(v, int):
            return ':int'
        if isinstance(v, float):
            return ':float'
        return ''

    for item_name, item_value in value.items():
        if isinstance(item_value, unicode):
            item_value = item_value.encode('utf-8')

        if isinstance(item_value, list) or isinstance(item_value, tuple):
            for item_subvalue in item_value:
                marshall_type = guess_type(item_subvalue)
                if isinstance(item_subvalue, bool):
                    item_subvalue = item_subvalue and '1' or ''
                encoded_name = '{0}.{1}{2}:list:{3}'.format(
                    prefix,
                    item_name,
                    marshall_type,
                    postfix
                )
                yield encoded_name, item_subvalue
        else:
            marshall_type = guess_type(item_value)
            if isinstance(item_value, bool):
                item_value = item_value and '1' or ''
            encoded_name = '{0:s}.{1:s}{2:s}:{3:s}'.format(
                prefix,
                item_name,
                marshall_type,
                postfix
            )
            yield encoded_name, item_value


def encode(data, schema, ignore=()):
    """Given a data dictionary with key/value pairs and schema, return an
    encoded query string. This is similar to urllib.urlencode(), but field
    names will include the appropriate field type converters, e.g. an int
    field will be encoded as fieldname:int=123. Fields not found in the data
    dict will be ignored, and items in the dict not in the schema will also
    be ignored. Additional fields to ignore can be passed with the 'ignore'
    parameter. If any fields cannot be converted, a ComponentLookupError
    will be raised.
    """

    encode = []

    for name, field in getFieldsInOrder(schema):
        if name in ignore or name not in data:
            continue

        converter = IFieldTypeConverter(field, None)
        if converter is None:
            raise ComponentLookupError(
                u'Cannot URL encode {0} of type {1}'.format(
                    name,
                    field.__class__
                )
            )

        encoded_name = name
        if converter.token:
            encoded_name = ':'.join([name, converter.token])

        value = data[name]
        if value is None:
            continue
        elif isinstance(value, unicode):
            value = value.encode('utf-8')

        if ISequence.providedBy(field):
            value_type_converter = IFieldTypeConverter(field.value_type, None)
            if value_type_converter is None:
                raise ComponentLookupError(
                    u'Cannot URL encode value type for {0} of type '
                    u'{1} : {2}'.format(
                        name,
                        field.__class__,
                        field.value_type.__class__
                    )
                )

            if value_type_converter.token:
                encoded_name = ':'.join([
                    name,
                    value_type_converter.token,
                    converter.token
                ])

            for item in value:

                if isinstance(item, bool):
                    item = item and '1' or ''

                if isinstance(item, dict):
                    encode.extend(map_to_pairs(encoded_name, item))
                else:
                    encode.append((encoded_name, item,))

        else:
            # The :bool converter just does bool() value, but urlencode() does
            # str() on the object. The result is False => 'False' => True :(
            if isinstance(value, bool):
                value = value and '1' or ''

            if isinstance(value, dict):
                encode.extend(map_to_pairs(encoded_name, value))
            else:
                encode.append((encoded_name, value))

    return urllib.urlencode(encode)


# Decoding

def decode(data, schema, missing=True):
    """Decode a data dict according to a schema. The returned dictionary will
    contain only keys matching schema names, and will force type values
    appropriately.

    This function is only necessary because the encoders used by encode()
    are not sufficiently detailed to always return the exact type expected
    by a field, e.g. resulting in ascii/unicode discrepancies.

    If missing is True, fields that are in the schema but not in the data will
    be set to field.missing_value. Otherwise, they are ignored.
    """

    decoded = {}

    for name, field in getFields(schema).items():
        if name not in data:
            if missing:
                decoded[name] = field.missing_value
            continue

        value = data[name]
        if value is None:
            continue

        field_type = field._type
        if isinstance(field_type, (tuple, list,)):
            field_type = field_type[-1]

        if ISequence.providedBy(field):
            converted = []

            value_type_field_type = field.value_type._type
            if isinstance(value_type_field_type, (tuple, list,)):
                value_type_field_type = value_type_field_type[-1]

            for item in value:
                if isinstance(item, str):
                    value = unicode(item, 'utf-8')
                if field.value_type._type and not isinstance(
                        item, field.value_type._type):
                    item = value_type_field_type(item)
                converted.append(item)

            value = converted
        elif isinstance(value, (tuple, list)) and value:
            value = value[0]

        if isinstance(value, str):
            value = unicode(value, 'utf-8')

        if field._type is not None and not isinstance(value, field._type):
            value = field_type(value)

        decoded[name] = value

    return decoded
