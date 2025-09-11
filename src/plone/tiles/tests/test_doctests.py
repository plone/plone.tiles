from plone.testing import layered
from plone.tiles.testing import PLONE_TILES_INTEGRATION_TESTING

import doctest
import re
import unittest


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        want = re.sub("u'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    return unittest.TestSuite(
        (
            layered(
                doctest.DocFileSuite(
                    "../tiles.rst",
                    "../directives.rst",
                    "../data.rst",
                    "../esi.rst",
                    optionflags=doctest.ELLIPSIS,
                    checker=Py23DocChecker(),
                ),
                layer=PLONE_TILES_INTEGRATION_TESTING,
            ),
        )
    )
