import unittest

from zope.testing import doctestunit
from zope.component import testing

# Test data - we put it here to allow proper dotted names in the test.

from zope.interface import Interface
from zope import schema

class IMailSettings(Interface):
    """Settings for email
    """
    
    sender = schema.TextLine(title=u"Mail sender", default=u"root@localhost")
    smtp_host = schema.URI(title=u"SMTP host server")

def test_suite():
    return unittest.TestSuite([
        doctestunit.DocFileSuite(
            'registry.txt', package='plone.registry',
            setUp=testing.setUp, tearDown=testing.tearDown),
        ])
