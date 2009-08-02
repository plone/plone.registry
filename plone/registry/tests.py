import unittest
import doctest

from zope.testing import doctestunit
from zope.component import provideAdapter, testing, eventtesting

from plone.registry.fieldfactory import persistentFieldAdapter
from plone.registry.fieldfactory import choicePersistentFieldAdapter

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
    
    provideAdapter(persistentFieldAdapter)
    provideAdapter(choicePersistentFieldAdapter)

class TestBugs(unittest.TestCase):
    """Regression tests for bugs that have been fixed
    """
    
    def setUp(self):
        setUp(self)
        
    def tearDown(self):
        testing.tearDown(self)
    
    def test_bind_choice(self):
        from plone.registry.field import Choice
        
        from zope.schema.vocabulary import getVocabularyRegistry
        from zope.schema.vocabulary import SimpleVocabulary
        
        def vocabFactory(obj):
            return SimpleVocabulary.fromValues(['one', 'two'])
        
        reg = getVocabularyRegistry()
        reg.register('my.vocab', vocabFactory)
        
        class T(object):
            f = None
        
        f = Choice(__name__='f', title=u"Test", vocabulary="my.vocab")
        t = T()
        
        # Bug: this would give "AttributeError: can't set attribute" on
        # clone.vocabulary
        f.bind(t)

        

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
        unittest.makeSuite(TestBugs),
        ])
