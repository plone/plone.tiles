======================
Data encoding/decoding
======================

This test exercises the ``encode()`` and ``decode()`` methods in
``plone.tiles.data``.

    >>> from zope.interface import Interface
    >>> from zope import schema

    >>> from plone.tiles.data import encode, decode

Encoding
--------

First, we'll create a simple schema that exercises several field types:

    >>> weekdays = [u'Monday', u'Tuesday', u'Wednesday', u'Thursday',
    ...             u'Friday', u'Saturday', u'Sunday']
    >>> class ISimple(Interface):
    ...     text_line   = schema.TextLine(title=u"Text")
    ...     ascii_line  = schema.ASCIILine(title=u"ASCII")
    ...     text        = schema.Text(title=u"Text", missing_value=u"Missing")
    ...     ascii       = schema.ASCII(title=u"ASCII")
    ...     int         = schema.Int(title=u"Int")
    ...     float       = schema.Float(title=u"Float")
    ...     bool        = schema.Bool(title=u"Bool")
    ...     weekday     = schema.Choice(title=u"Weekday", values=weekdays)
    ...     list        = schema.List(value_type=schema.TextLine())
    ...     listchoice  = schema.List(value_type=schema.Choice(vocabulary='foobar'))

A simple encode produces a query string:

    >>> data = dict(text_line=u'A', ascii_line='B', text=u'C\nD', ascii='E\nF', int=3, float=1.2, bool=False, weekday=u'Saturday')
    >>> encode(data, ISimple)
    'text_line=A&ascii_line=B&text%3Atext=C%0AD&ascii%3Atext=E%0AF&int%3Along=3&float%3Afloat=1.2&bool%3Aboolean=&weekday=Saturday'

Notice how a boolean is encoded as an empty value. If it were true, it'd be
encoded as 1:

    >>> data = dict(text_line=u'A', ascii_line='B', text=u'C\nD', ascii='E\nF', int=3, float=1.2, bool=True, weekday=u'Saturday')
    >>> encode(data, ISimple)
    'text_line=A&ascii_line=B&text%3Atext=C%0AD&ascii%3Atext=E%0AF&int%3Along=3&float%3Afloat=1.2&bool%3Aboolean=1&weekday=Saturday'

If the data dictionary has values not in the interface, they are ignored:

    >>> data = dict(text_line=u'A', ascii_line='B', text=u'C\nD', ascii='E\nF', int=3, float=1.2, bool=True, weekday=u'Saturday', foo=123)
    >>> encode(data, ISimple)
    'text_line=A&ascii_line=B&text%3Atext=C%0AD&ascii%3Atext=E%0AF&int%3Along=3&float%3Afloat=1.2&bool%3Aboolean=1&weekday=Saturday'

If the data dictionary omits some fields, they are ignored.

    >>> data = dict(text_line=u'A', ascii_line='B', text=u'C\nD', ascii='E\nF', float=1.2, bool=True, foo=123)
    >>> encode(data, ISimple)
    'text_line=A&ascii_line=B&text%3Atext=C%0AD&ascii%3Atext=E%0AF&float%3Afloat=1.2&bool%3Aboolean=1'

It is also possible to explicitly ignore some fields:

    >>> data = dict(text_line=u'A', ascii_line='B', text=u'C\nD', ascii='E\nF', float=1.2, bool=True, foo=123)
    >>> encode(data, ISimple, ignore=('text_line', 'text',))
    'ascii_line=B&ascii%3Atext=E%0AF&float%3Afloat=1.2&bool%3Aboolean=1'

Lists and tuples may also be encoded. The value type will be encoded as well.

    >>> class ISequences(Interface):
    ...     list    = schema.List(title=u"List", value_type=schema.ASCIILine(title=u"Text"))
    ...     tuple   = schema.Tuple(title=u"List", value_type=schema.Int(title=u"Int"))

    >>> data = dict(list=['a', 'b'], tuple=(1,2,3))
    >>> encode(data, ISequences)
    'list%3Alist=a&list%3Alist=b&tuple%3Along%3Atuple=1&tuple%3Along%3Atuple=2&tuple%3Along%3Atuple=3'

Even dictionaries may be encoded. And the value type will be encoded as well.

    >>> class IRecords(Interface):
    ...     record = schema.Dict(title=u"Record")
    ...     records = schema.List(title=u"Records", value_type=schema.Dict())

    >>> data = dict(record={'a': 'b', 'c': True}, records=[{'a': 'b', 'c': True}])
    >>> encode(data, IRecords)
    'record.a%3Arecord=b&record.c%3Aboolean%3Arecord=1&records.a%3Arecords=b&records.c%3Aboolean%3Arecords=1'

Unsupported fields will raise a ComponentLookupError. This also
applies to the value_type of a list or tuple:

    >>> class IUnsupported(Interface):
    ...     decimal     = schema.Decimal(title=u"Decimal")
    ...     list        = schema.List(title=u"Set", value_type=schema.Decimal(title=u"Decimal"))
    ...     bytes_line  = schema.BytesLine(title=u"Bytes line")

    >>> from decimal import Decimal
    >>> data = dict(decimal=Decimal(2), list=[Decimal(1), Decimal(2),], bytes_line='abc')
    >>> encode(data, IUnsupported) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ComponentLookupError: Cannot URL encode decimal of type <class 'zope.schema._field.Decimal'>

    >>> encode(data, IUnsupported, ignore=('decimal',)) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ComponentLookupError: Cannot URL encode value type for list of type <class 'zope.schema._field.List'> : <class 'zope.schema._field.Decimal'>

    >>> encode(data, IUnsupported, ignore=('decimal', 'list',))
    'bytes_line=abc'

Decoding
--------

The decoder exists because the Zope form marshalers are not perfect: for
instance, they cannot adequately deal with the differences between unicode
and ASCII. ``zope.schema`` is picky about that sort of thing.

Let's use a data dictionary that may have come back from a query string like
the first example above.

    >>> data = dict(text_line=u'A', ascii_line=u'B', text=u'C\nD', ascii=u'E\nF', int=3, float=1.2, bool=False, weekday=u'Saturday')
    >>> sorted(decode(data, ISimple).items())
    [('ascii', 'E\nF'), ('ascii_line', 'B'), ('bool', False), ('float', 1.2), ('int', 3), ('list', None), ('listchoice', None), ('text', u'C\nD'), ('text_line', u'A'), ('weekday', u'Saturday')]

If any values are missing from the input dictionary, they will default to
``missing_value``.

    >>> data = dict(text_line=u'A', ascii_line=u'B', int=3, float=1.2, bool=False, weekday=u'Saturday')
    >>> sorted(decode(data, ISimple).items())
    [('ascii', None), ('ascii_line', 'B'), ('bool', False), ('float', 1.2), ('int', 3), ('list', None), ('listchoice', None), ('text', u'Missing'), ('text_line', u'A'), ('weekday', u'Saturday')]

If you pass ``missing=False``, the values are ignored instead.

    >>> data = dict(text_line=u'A', ascii_line=u'B', int=3, float=1.2, bool=False)
    >>> sorted(decode(data, ISimple, missing=False).items())
    [('ascii_line', 'B'), ('bool', False), ('float', 1.2), ('int', 3), ('text_line', u'A')]

Decoding also works for lists and their value types:

    >>> data = dict(list=[u'a', u'b'])
    >>> sorted(decode(data, ISequences, missing=False).items())
    [('list', ['a', 'b'])]

Decoding should work with lists and the ISimple schema

    >>> data = dict(list=['a', 'b'])
    >>> sorted(decode(data, ISimple, missing=False).items())
    [('list', [u'a', u'b'])]

And list choice fields

    >>> data = dict(listchoice=['a', 'b'])
    >>> sorted(decode(data, ISimple, missing=False).items())
    [('listchoice', ['a', 'b'])]
