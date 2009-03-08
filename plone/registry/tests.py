import unittest
import doctest

from zope.testing import doctestunit
from zope.component import provideAdapter, testing, eventtesting

from plone.registry.fieldfactory import persistent_field_adapter
from plone.registry.fieldfactory import choice_persistent_field_adapter

from zope.interface import Interface
from zope import schema

class IMailSettings(Interface):
    """Settings for email
    """
    
    sender = schema.TextLine(title=u"Mail sender", default=u"root@localhost")
    smtp_host = schema.URI(title=u"SMTP host server")

class IMailPreferences(Interface):
    """Settings for email
    """
    
    max_daily = schema.Int(title=u"Maximum number of emails per day", min=0, default=3)
    settings = schema.Object(title=u"Mail setings to use", schema=IMailSettings)

def setUp(test=None):
    testing.setUp()
    eventtesting.setUp()
    
    provideAdapter(persistent_field_adapter)
    provideAdapter(choice_persistent_field_adapter)

def test_suite():
    return unittest.TestSuite([
        doctestunit.DocFileSuite(
            'registry.txt', package='plone.registry',
            optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            setUp=setUp, tearDown=testing.tearDown),
        doctestunit.DocFileSuite(
            'events.txt', package='plone.registry',
            optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            setUp=setUp, tearDown=testing.tearDown),
        doctestunit.DocFileSuite(
            'field.txt', package='plone.registry',
            optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            setUp=setUp, tearDown=testing.tearDown),
        ])
