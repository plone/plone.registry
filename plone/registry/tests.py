# -*- coding: utf-8 -*-
from plone.registry.fieldfactory import choicePersistentFieldAdapter
from plone.registry.fieldfactory import persistentFieldAdapter
from plone.registry.recordsproxy import ComplexRecordsProxy
from plone.registry.registry import Registry
from zope import schema
from zope.component import eventtesting
from zope.component import provideAdapter
from zope.component import testing
from zope.interface import Interface
from zope.interface import implementer
from zope.testing import doctestunit
import doctest
import unittest


class IMailSettings(Interface):
    """Settings for email
    """

    sender = schema.TextLine(title=u"Mail sender", default=u"root@localhost")
    smtp_host = schema.URI(title=u"SMTP host server")


class IMailPreferences(Interface):
    """Settings for email
    """
    max_daily = schema.Int(
        title=u"Maximum number of emails per day",
        min=0,
        default=3
    )
    settings = schema.Object(
        title=u"Mail setings to use",
        schema=IMailSettings
    )

class ISimpleSettings(Interface):
    """ A very simple schmema for testing purposes
    """

    number = schema.Int(title=u"A number")


class IComplexPreferences(Interface):
    """ Complex settings with an object and a collection of objects
    """
    complex_collection = schema.Tuple(
        value_type=schema.Object(
            schema=IMailSettings))

    complex_type = schema.Object(schema=ISimpleSettings)


@implementer(IMailSettings)
class MailSettings(object):

    def __init__(self, sender, smtp_host):
        self.sender = sender
        self.smtp_host = smtp_host


@implementer(ISimpleSettings)
class SimpleSettings(object):

    def __init__(self, number):
        self.number = number


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

    def test_fieldref_interfaces(self):
        from plone.registry import field, FieldRef
        from plone.registry.interfaces import IFieldRef
        from zope.schema.interfaces import ICollection

        listField = field.List(value_type=field.ASCIILine())
        ref = FieldRef('some.record', listField)

        self.assertTrue(ICollection.providedBy(ref))
        self.assertTrue(IFieldRef.providedBy(ref))


class TestMigration(unittest.TestCase):

    def setUp(self):
        setUp(self)

    def tearDown(self):
        testing.tearDown(self)

    def test_auto_migration(self):

        from BTrees.OOBTree import OOBTree

        from plone.registry.registry import Registry, Records, _Records
        from plone.registry.record import Record
        from plone.registry import field

        # Create an "old-looking registry"

        registry = Registry()
        registry._records = Records(registry)
        registry._records.data = OOBTree()

        f = field.TextLine(title=u"Foo")

        record = Record(f, u"Bar")
        record.__dict__['field'] = f
        record.__dict__['value'] = u"Bar"

        registry._records.data['foo.bar'] = record

        # Attempt to access it

        value = registry['foo.bar']

        # Migration should have happened

        self.assertEqual(value, u"Bar")
        self.assertEqual(registry.records['foo.bar'].field.title, u"Foo")
        self.assertEqual(registry.records['foo.bar'].value, u"Bar")

        self.assertFalse(isinstance(registry._records, Records))
        self.assertTrue(isinstance(registry._records, _Records))


class TestProxy(unittest.TestCase):

    def setUp(self):
        setUp(self)
        self.registry = Registry()
        self.cfp = ComplexRecordsProxy(self.registry, IComplexPreferences)

    def test_complexrecordsproxy(self):
        self.cfp.complex_type = SimpleSettings(9)
        self.assertEqual(
             repr(self.cfp.complex_type),
             '<ComplexRecordsProxy for plone.registry.tests.ISimpleSettings>')
        self.assertEqual(self.cfp.complex_type.number, 9)

    def test_complexrecordsproxy_collection(self):
        self.cfp.complex_collection = (
            MailSettings(u'test@example.org', 'http://www.example.org'),
            MailSettings(u'info@example.com', 'http://www.example.com'))
        self.assertEqual(
            repr(self.cfp.complex_collection),
            ('[<ComplexRecordsProxy for plone.registry.tests.IMailSettings>, '
             '<ComplexRecordsProxy for plone.registry.tests.IMailSettings>]'))
        self.assertEqual(self.cfp.complex_collection[0].smtp_host,
                         'http://www.example.org')
        self.assertRaises(AttributeError, getattr, self.cfp, 'bogusattr')


def test_suite():
    return unittest.TestSuite([
        doctestunit.DocFileSuite(
            'registry.rst',
            package='plone.registry',
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            setUp=setUp,
            tearDown=testing.tearDown
        ),
        doctestunit.DocFileSuite(
            'events.rst',
            package='plone.registry',
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            setUp=setUp,
            tearDown=testing.tearDown
        ),
        doctestunit.DocFileSuite(
            'field.rst',
            package='plone.registry',
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            setUp=setUp,
            tearDown=testing.tearDown
        ),
        unittest.makeSuite(TestBugs),
        unittest.makeSuite(TestMigration),
        unittest.makeSuite(TestProxy),
    ])
