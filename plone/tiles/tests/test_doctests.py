# -*- coding: utf-8 -*-
from plone.testing import layered
from plone.tiles.testing import PLONE_TILES_INTEGRATION_TESTING

import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        layered(
            doctest.DocFileSuite(
                '../tiles.rst',
                '../directives.rst',
                '../data.rst',
                '../esi.rst',
                optionflags=doctest.ELLIPSIS
            ),
            layer=PLONE_TILES_INTEGRATION_TESTING
        ),
    ))
