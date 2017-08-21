# -*- coding: utf-8 -*-
from plone.rfc822.interfaces import IPrimaryField
from plone.tiles.data import decode
from plone.tiles.data import encode
from plone.tiles.testing import PLONE_TILES_INTEGRATION_TESTING
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface

import unittest


class IQuerySchema(Interface):

    query = schema.List(
        title=u'Search terms',
        value_type=schema.Dict(value_type=schema.Field(),
                               key_type=schema.TextLine()),
        required=False
    )

    lines = schema.List(
        title=u'Strings',
        value_type=schema.TextLine(),
        required=False
    )

    title = schema.TextLine(
        title=u'Title'
    )


class IWords(Interface):

    words = schema.List(
        title=u'Words',
        value_type=schema.TextLine(),
        required=False
    )


class IPrimary(Interface):

    words = schema.List(
        title=u'Words',
        value_type=schema.TextLine(),
        required=False
    )

alsoProvides(IPrimary['words'], IPrimaryField)


class TestEncode(unittest.TestCase):

    layer = PLONE_TILES_INTEGRATION_TESTING

    def test_encode_querystring_special(self):
        data = {
            'query': [{'i': 'Subject',
                       'o': 'plone.app.querystring.operation.selection.any',
                       'v': [u'äüö']}],
            'title': u'Hello World'
        }
        self.assertEqual(
            encode(data, schema=IQuerySchema),
            ('query.i%3Arecords=Subject&query.o%3A'
             'records=plone.app.querystring.operation.selection.any&'
             'query.v%3Alist%3Arecords=%C3%A4%C3%BC%C3%B6&title=Hello+World')
        )

    def test_encode_unicode_lines(self):
        data = {
            'words': [u'ä', u'ö']
        }
        self.assertEqual(
            encode(data, schema=IWords),
            'words%3Alist=%C3%A4&words%3Alist=%C3%B6'
        )

    def test_skip_encoding_primary_fields(self):
        data = {
            'words': [u'ä', u'ö']
        }
        self.assertEqual(
            encode(data, schema=IPrimary),
            ''
        )


class TestDecode(unittest.TestCase):

    layer = PLONE_TILES_INTEGRATION_TESTING

    def test_decode_unicode_lines(self):
        data = {
            'words': [u'ä', u'ö']
        }
        self.assertEqual(
            decode(data, schema=IWords),
            {
                'words': [u'ä', u'ö']
            }
        )

    def test_skip_decoding_primary_fields(self):
        data = {
            'words': [u'ä', u'ö']
        }
        self.assertEqual(
            decode(data, schema=IPrimary),
            {}
        )
