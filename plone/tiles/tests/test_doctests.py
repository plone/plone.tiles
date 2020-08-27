# -*- coding: utf-8 -*-
from plone.testing import layered
from plone.tiles.testing import PLONE_TILES_INTEGRATION_TESTING

import doctest
import re
import six
import unittest


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            # In Py 3 we get the full class path, in Py 2 only the class.
            # The tests have the full path.
            want = re.sub(
                'zope.interface.interfaces.ComponentLookupError',
                'ComponentLookupError',
                want)
            want = re.sub(
                'zExceptions.unauthorized.Unauthorized', 'Unauthorized', want)
            got = re.sub("u'(.*?)'", "'\\1'", got)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    return unittest.TestSuite((
        layered(
            doctest.DocFileSuite(
                '../tiles.rst',
                '../directives.rst',
                '../data.rst',
                '../esi.rst',
                optionflags=doctest.ELLIPSIS,
                checker=Py23DocChecker(),
            ),
            layer=PLONE_TILES_INTEGRATION_TESTING
        ),
    ))
