import unittest

import zope.testing.doctest
import zope.app.testing.placelesssetup

def test_suite():
    return unittest.TestSuite((
        
        zope.testing.doctest.DocFileSuite('tiles.txt',
                     setUp=zope.app.testing.placelesssetup.setUp,
                     tearDown=zope.app.testing.placelesssetup.tearDown),

        zope.testing.doctest.DocFileSuite('directives.txt',
                     setUp=zope.app.testing.placelesssetup.setUp,
                     tearDown=zope.app.testing.placelesssetup.tearDown),

        zope.testing.doctest.DocFileSuite('data.txt',
                     setUp=zope.app.testing.placelesssetup.setUp,
                     tearDown=zope.app.testing.placelesssetup.tearDown),

        ))
