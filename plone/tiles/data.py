# -*- coding: utf-8 -*-
from persistent.dict import PersistentDict
from plone.subrequest import ISubRequest
from plone.tiles.directives import IGNORE_QUERYSTRING_KEY
from plone.tiles.interfaces import IFieldTypeConverter
from plone.tiles.interfaces import IPersistentTile
from plone.tiles.interfaces import ITile
from plone.tiles.interfaces import ITileDataContext
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileDataStorage
from plone.tiles.interfaces import ITileType
from six.moves.urllib import parse
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interfaces import ComponentLookupError
from zope.schema import getFields
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import ISequence

import json
import logging
import pkg_resources
import six


try:
    pkg_resources.get_distribution('plone.rfc822')
except pkg_resources.DistributionNotFound:
    HAS_RFC822 = False
else:
    from plone.rfc822.interfaces import IPrimaryField
    HAS_RFC822 = True


ANNOTATIONS_KEY_PREFIX = u'plone.tiles.data'
LOGGER = logging.getLogger('plone.tiles')


@adapter(ITile)
@implementer(ITileDataManager)
def transientTileDataManagerFactory(tile):
    if tile.request.get('X-Tile-Persistent'):
        return PersistentTileDataManager(tile)
    else:
        return TransientTileDataManager(tile)


class BaseTileDataManager(object):

    def get_default_request_data(self):
        """
        from request form
        """
        # try to use a '_tiledata' parameter in the request
        if '_tiledata' in self.tile.request.form:
            data = json.loads(self.tile.request.form['_tiledata'])
        elif self.tileType is None or self.tileType.schema is None:
            data = self.tile.request.form.copy()
        else:
            # Try to decode the form data properly if we can
            try:
                data = decode(self.tile.request.form,
                              self.tileType.schema,
                              missing=True, primary=True)
            except (ValueError, UnicodeDecodeError,):
                LOGGER.exception(u'Could not convert form data to schema')
                return self.data.copy()
        # we're assuming this data is potentially unsafe so we need to check
        # the ignore querystring field setting

        # before we start, we allow it for sub-requests since in this case,
        # the input is safe and we can trust it
        if ISubRequest.providedBy(self.tile.request):
            return data

        # first off, we only care to filter if it is a GET request
        if getattr(self.tile.request, 'REQUEST_METHOD', 'GET') != 'GET':
            return data

        # now, pay attention to schema hints for form data
        if self.tileType is not None and self.tileType.schema is not None:
            for name in self.tileType.schema.queryTaggedValue(
                    IGNORE_QUERYSTRING_KEY) or []:
                if name in data:
                    del data[name]

        return data


@adapter(ITile)
@implementer(ITileDataManager)
class TransientTileDataManager(BaseTileDataManager):
    """A data manager for transient tile data, which reads data from the
    request query string.
    """

    def __init__(self, tile):
        self.tile = tile
        self.tileType = queryUtility(ITileType, name=tile.__name__)

        self.context = getMultiAdapter(
            (tile.context, tile.request, tile), ITileDataContext)
        self.storage = getMultiAdapter(
            (self.context, tile.request, tile), ITileDataStorage)

        if IAnnotations.providedBy(self.storage):
            self.key = '.'.join([ANNOTATIONS_KEY_PREFIX, str(tile.id)])
        else:
            self.key = str(tile.id)

    @property
    def annotations(self):  # BBB for < 0.7.0 support
        return self.storage

    def get(self):
        # use explicitly set data (saved as annotation on the request)
        if self.key in self.storage:
            data = dict(self.storage[self.key])

            if self.tileType is not None and self.tileType.schema is not None:
                for name, field in getFields(self.tileType.schema).items():
                    if name not in data:
                        data[name] = field.missing_value
        # fall back to the copy of request.form object itself
        else:
            data = self.get_default_request_data()

        return data

    def set(self, data):
        self.storage[self.key] = data

    def delete(self):
        if self.key in self.storage:
            self.storage[self.key] = {}


@adapter(IPersistentTile)
@implementer(ITileDataManager)
class PersistentTileDataManager(BaseTileDataManager):
    """A data reader for persistent tiles operating on annotatable contexts.
    The data is retrieved from an annotation.
    """

    def __init__(self, tile):
        self.tile = tile
        self.tileType = queryUtility(ITileType, name=tile.__name__)

        self.context = getMultiAdapter(
            (tile.context, tile.request, tile), ITileDataContext)
        self.storage = getMultiAdapter(
            (self.context, tile.request, tile), ITileDataStorage)

        if IAnnotations.providedBy(self.storage):
            self.key = '.'.join([ANNOTATIONS_KEY_PREFIX, str(tile.id)])
        else:
            self.key = str(tile.id)

    @property
    def annotations(self):  # BBB for < 0.7.0 support
        return self.storage

    def get(self):
        data = self.get_default_request_data()
        data.update(dict(self.storage.get(self.key, {})))
        if self.tileType is not None and self.tileType.schema is not None:
            for name, field in getFields(self.tileType.schema).items():
                if name not in data:
                    data[name] = field.missing_value
        return data

    def set(self, data):
        self.storage[self.key] = PersistentDict(data)

    def delete(self):
        if self.key in self.storage:
            del self.storage[self.key]


@implementer(ITileDataContext)
@adapter(Interface, Interface, ITile)
def defaultTileDataContext(context, request, tile):
    return tile.context


@implementer(ITileDataStorage)
@adapter(Interface, Interface, ITile)
def defaultTileDataStorage(context, request, tile):
    if tile.request.get('X-Tile-Persistent'):
        return defaultPersistentTileDataStorage(context, request, tile)
    else:
        return IAnnotations(tile.request, tile.request.form)


@implementer(ITileDataStorage)
@adapter(Interface, Interface, IPersistentTile)
def defaultPersistentTileDataStorage(context, request, tile):
    return IAnnotations(context)


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
        if isinstance(item_value, six.text_type):
            item_value = item_value.encode('utf-8')

        if isinstance(item_value, list) or isinstance(item_value, tuple):
            for item_subvalue in item_value:
                marshall_type = guess_type(item_subvalue)
                if isinstance(item_subvalue, bool):
                    item_subvalue = item_subvalue and '1' or ''
                elif isinstance(item_subvalue, six.text_type):
                    item_subvalue = item_subvalue.encode('utf-8')
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
            elif isinstance(item_value, six.text_type):
                item_value = item_value.encode('utf-8')
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
        if HAS_RFC822 and IPrimaryField.providedBy(field):
            continue

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
        elif isinstance(value, six.text_type):
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
                elif isinstance(item, six.text_type):
                    item = item.encode('utf-8')

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

    return parse.urlencode(encode)


# Decoding

def decode(data, schema, missing=True, primary=False):
    """Decode a data dict according to a schema. The returned dictionary will
    contain only keys matching schema names, and will force type values
    appropriately.

    This function is only necessary because the encoders used by encode()
    are not sufficiently detailed to always return the exact type expected
    by a field, e.g. resulting in ascii/unicode discrepancies.

    If missing is True, fields that are in the schema but not in the data will
    be set to field.missing_value. Otherwise, they are ignored.

    If primary is True, also fields that are marged as primary fields are
    decoded from the data. (Primary fields are not decoded by default,
    because primary field are mainly used for rich text or binary fields
    and data is usually parsed from query string with length limitations.)
    """

    decoded = {}

    for name, field in getFields(schema).items():
        if not primary and HAS_RFC822 and IPrimaryField.providedBy(field):
            continue

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
                if field.value_type._type and not isinstance(
                        item, field.value_type._type):
                    item = value_type_field_type(item)
                converted.append(item)

            value = converted
        elif isinstance(value, (tuple, list)) and value:
            value = value[0]

        if isinstance(value, six.binary_type):
            value = value.decode('utf-8')

        if field._type is not None and not isinstance(value, field._type):
            value = field_type(value)

        decoded[name] = value

    return decoded
