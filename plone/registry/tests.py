import unittest

from zope.testing import doctestunit
from zope.component import testing

def test_suite():
    return unittest.TestSuite([
        doctestunit.DocFileSuite(
            'registry.txt', package='plone.registry',
            setUp=testing.setUp, tearDown=testing.tearDown),
        ])
