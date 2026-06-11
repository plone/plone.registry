from plone.registry.fieldfactory import choicePersistentFieldAdapter
from plone.registry.fieldfactory import persistentFieldAdapter
from zope import schema
from zope.component import eventtesting
from zope.component import provideAdapter
from zope.component import testing
from zope.interface import Interface

import doctest
import re
import unittest

IGNORE_U = doctest.register_optionflag("IGNORE_U")


class PolyglotOutputChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        # fix changed objectfield class in zope4
        got = re.sub(
            "zope.schema._field.Object", "zope.schema._bootstrapfields.Object", got
        )

        if hasattr(self, "_toAscii"):
            got = self._toAscii(got)
            want = self._toAscii(want)

        # Naive fix for comparing byte strings
        if got != want and optionflags & IGNORE_U:
            got = re.sub(r'^u([\'"])', r"\1", got)
            want = re.sub(r'^u([\'"])', r"\1", want)

        return doctest.OutputChecker.check_output(self, want, got, optionflags)


class IMailSettings(Interface):
    """Settings for email"""

    sender = schema.TextLine(title="Mail sender", default="root@localhost")
    smtp_host = schema.URI(title="SMTP host server")


class IMailPreferences(Interface):
    """Settings for email"""

    max_daily = schema.Int(title="Maximum number of emails per day", min=0, default=3)
    settings = schema.Object(title="Mail settings to use", schema=IMailSettings)


def setUp(test=None):
    testing.setUp()
    eventtesting.setUp()

    provideAdapter(persistentFieldAdapter)
    provideAdapter(choicePersistentFieldAdapter)


class TestBugs(unittest.TestCase):
    """Regression tests for bugs that have been fixed"""

    def setUp(self):
        setUp(self)

    def tearDown(self):
        testing.tearDown(self)

    def test_bind_choice(self):
        from plone.registry.field import Choice
        from zope.schema.vocabulary import getVocabularyRegistry
        from zope.schema.vocabulary import SimpleVocabulary

        def vocabFactory(obj):
            return SimpleVocabulary.fromValues(["one", "two"])

        reg = getVocabularyRegistry()
        reg.register("my.vocab", vocabFactory)

        class T:
            f = None

        f = Choice(__name__="f", title="Test", vocabulary="my.vocab")
        t = T()

        # Bug: this would give "AttributeError: can't set attribute" on
        # clone.vocabulary
        f.bind(t)

    def test_fieldref_interfaces(self):
        from plone.registry import field
        from plone.registry import FieldRef
        from plone.registry.interfaces import IFieldRef
        from zope.schema.interfaces import ICollection

        listField = field.List(value_type=field.ASCIILine())
        ref = FieldRef("some.record", listField)

        self.assertTrue(ICollection.providedBy(ref))
        self.assertTrue(IFieldRef.providedBy(ref))


class TestMigration(unittest.TestCase):
    def setUp(self):
        setUp(self)

    def tearDown(self):
        testing.tearDown(self)

    def test_auto_migration(self):
        from BTrees.OOBTree import OOBTree
        from plone.registry import field
        from plone.registry.record import Record
        from plone.registry.registry import _Records
        from plone.registry.registry import Records
        from plone.registry.registry import Registry

        # Create an "old-looking registry"

        registry = Registry()
        registry._records = Records(registry)
        registry._records.data = OOBTree()

        f = field.TextLine(title="Foo")

        record = Record(f, "Bar")
        record.__dict__["field"] = f
        record.__dict__["value"] = "Bar"

        registry._records.data["foo.bar"] = record

        # Attempt to access it

        value = registry["foo.bar"]

        # Migration should have happened

        self.assertEqual(value, "Bar")
        self.assertEqual(registry.records["foo.bar"].field.title, "Foo")
        self.assertEqual(registry.records["foo.bar"].value, "Bar")

        self.assertFalse(isinstance(registry._records, Records))
        self.assertTrue(isinstance(registry._records, _Records))


class FakeRequest:
    """Minimal request-like object for testing request-level caching.

    Uses a dict (``other``) for item access, mirroring Zope's
    ``HTTPRequest.other`` which is cleared at end-of-request.
    """

    def __init__(self):
        self.environ = {}
        self.other = {}

    def get(self, key, default=None):
        return self.other.get(key, default)

    def __getitem__(self, key):
        return self.other[key]

    def __setitem__(self, key, value):
        self.other[key] = value

    def __contains__(self, key):
        return key in self.other


class TestRequestValueCache(unittest.TestCase):
    """Tests for request-level value caching in Registry."""

    def setUp(self):
        setUp(self)
        from plone.registry import field
        from plone.registry.record import Record
        from plone.registry.registry import Registry

        self.registry = Registry()
        self.registry.records["test.key1"] = Record(
            field.TextLine(title="Key 1"), "value1"
        )
        self.registry.records["test.key2"] = Record(
            field.TextLine(title="Key 2"), "value2"
        )
        self.registry.records["test.none"] = Record(
            field.TextLine(title="None val", required=False), None
        )
        self.request = FakeRequest()

    def tearDown(self):
        from zope.globalrequest import clearRequest

        clearRequest()
        testing.tearDown(self)

    def _setRequest(self):
        from zope.globalrequest import setRequest

        setRequest(self.request)

    def _getCache(self, request=None):
        """Return the per-registry cache dict from the given request."""
        if request is None:
            request = self.request
        all_caches = request.other.get("_plone_registry_cache", {})
        return all_caches.get(id(self.registry), {})

    def _setCache(self, data):
        """Inject values into the per-registry cache on the request."""
        self.request.other["_plone_registry_cache"] = {id(self.registry): data}

    def test_subscriber_sees_new_value(self):
        """A subscriber should see the new value even if the request cache exists."""
        from plone.registry.interfaces import IRecordModifiedEvent
        from zope.component import provideHandler

        self._setRequest()

        # Populate cache
        self.assertEqual(self.registry["test.key1"], "value1")

        seen_values = []

        def subscriber(event):
            # Try to read the value from the registry
            seen_values.append(self.registry["test.key1"])

        provideHandler(subscriber, (IRecordModifiedEvent,))

        # Update value
        self.registry["test.key1"] = "new_value"

        self.assertEqual(
            seen_values,
            ["new_value"],
            "Subscriber saw the old cached value instead of the new one",
        )

    # --- __getitem__ tests ---

    def test_getitem_no_request(self):
        """Without a request, values are fetched directly from OOBTree."""
        self.assertEqual(self.registry["test.key1"], "value1")
        self.assertNotIn("_plone_registry_cache", self.request)

    def test_getitem_populates_cache(self):
        """First read with a request populates the cache."""
        self._setRequest()
        self.assertEqual(self.registry["test.key1"], "value1")
        cache = self._getCache()
        self.assertIn("test.key1", cache)
        self.assertEqual(cache["test.key1"], "value1")

    def test_getitem_serves_from_cache(self):
        """Subsequent reads return the cached value."""
        self._setRequest()
        self._setCache({"test.key1": "cached_value"})
        self.assertEqual(self.registry["test.key1"], "cached_value")

    def test_getitem_keyerror_not_cached(self):
        """KeyError for missing keys propagates without caching."""
        self._setRequest()
        with self.assertRaises(KeyError):
            self.registry["nonexistent.key"]
        self.assertNotIn("nonexistent.key", self._getCache())

    def test_getitem_multiple_keys(self):
        """Multiple keys are independently cached."""
        self._setRequest()
        self.assertEqual(self.registry["test.key1"], "value1")
        self.assertEqual(self.registry["test.key2"], "value2")
        cache = self._getCache()
        self.assertEqual(cache["test.key1"], "value1")
        self.assertEqual(cache["test.key2"], "value2")

    # --- get() tests ---

    def test_get_no_request(self):
        """Without a request, get() works normally."""
        self.assertEqual(self.registry.get("test.key1"), "value1")
        self.assertEqual(self.registry.get("nonexistent", "default"), "default")

    def test_get_populates_cache(self):
        """get() populates the cache on first access."""
        self._setRequest()
        self.assertEqual(self.registry.get("test.key1"), "value1")
        self.assertIn("test.key1", self._getCache())

    def test_get_serves_from_cache(self):
        """get() returns cached value on subsequent access."""
        self._setRequest()
        self._setCache({"test.key1": "cached"})
        self.assertEqual(self.registry.get("test.key1"), "cached")

    def test_get_default_not_cached(self):
        """get() with missing key returns default and does not cache it."""
        self._setRequest()
        result = self.registry.get("nonexistent", "default")
        self.assertEqual(result, "default")
        self.assertNotIn("nonexistent", self._getCache())

    def test_get_none_value_cached(self):
        """None values are correctly cached (not confused with sentinel)."""
        self._setRequest()
        result = self.registry.get("test.none")
        self.assertIsNone(result)
        self.assertIn("test.none", self._getCache())
        self.assertIsNone(self.registry.get("test.none"))

    def test_get_none_default(self):
        """get() returns None default for missing keys without caching."""
        self._setRequest()
        result = self.registry.get("nonexistent")
        self.assertIsNone(result)
        self.assertNotIn("nonexistent", self._getCache())

    # --- __setitem__ tests ---

    def test_setitem_updates_cache(self):
        """Writing a value updates the cache."""
        self._setRequest()
        self.assertEqual(self.registry["test.key1"], "value1")
        self.registry["test.key1"] = "new_value"
        self.assertEqual(self._getCache()["test.key1"], "new_value")
        self.assertEqual(self.registry["test.key1"], "new_value")

    def test_setitem_no_request(self):
        """Writing without a request works normally."""
        self.registry["test.key1"] = "new_value"
        self.assertEqual(self.registry["test.key1"], "new_value")

    # --- Cache isolation ---

    def test_cache_isolation_between_requests(self):
        """Different requests have independent caches."""
        from zope.globalrequest import setRequest

        self._setRequest()
        self.registry["test.key1"]  # populate cache

        new_request = FakeRequest()
        setRequest(new_request)
        self.assertNotIn("_plone_registry_cache", new_request)

        self.assertEqual(self.registry["test.key1"], "value1")
        self.assertIn("test.key1", self._getCache(new_request))
        self.assertIn("test.key1", self._getCache(self.request))

    def test_cache_lazily_created(self):
        """Cache dict is only created on first registry access."""
        self._setRequest()
        self.assertNotIn("_plone_registry_cache", self.request)
        self.registry["test.key1"]
        self.assertIn("_plone_registry_cache", self.request)

    # --- __contains__ tests ---

    def test_contains_no_request(self):
        """Without a request, __contains__ works normally."""
        self.assertIn("test.key1", self.registry)
        self.assertNotIn("nonexistent", self.registry)

    def test_contains_uses_value_cache(self):
        """__contains__ returns True if key is in the value cache."""
        self._setRequest()
        self.registry.get("test.key1")
        self.assertIn("test.key1", self.registry)

    def test_contains_falls_through_to_oobtree(self):
        """__contains__ falls through to OOBTree for uncached keys."""
        self._setRequest()
        self.assertIn("test.key2", self.registry)
        self.assertNotIn("nonexistent", self.registry)


class TestForInterfaceCache(unittest.TestCase):
    """Tests for forInterface() proxy caching."""

    def setUp(self):
        setUp(self)
        from plone.registry.registry import Registry

        self.registry = Registry()
        self.registry.registerInterface(IMailSettings)
        self.request = FakeRequest()

    def tearDown(self):
        from zope.globalrequest import clearRequest

        clearRequest()
        testing.tearDown(self)

    def _setRequest(self):
        from zope.globalrequest import setRequest

        setRequest(self.request)

    def test_forinterface_no_request(self):
        """Without a request, forInterface works normally."""
        proxy = self.registry.forInterface(IMailSettings)
        self.assertTrue(IMailSettings.providedBy(proxy))

    def test_forinterface_caches_proxy(self):
        """With a request, forInterface caches the proxy."""
        self._setRequest()
        proxy1 = self.registry.forInterface(IMailSettings)
        proxy2 = self.registry.forInterface(IMailSettings)
        self.assertIs(proxy1, proxy2)

    def test_forinterface_cache_hit_skips_check(self):
        """Cached proxy avoids the field existence check."""
        self._setRequest()
        proxy1 = self.registry.forInterface(IMailSettings)
        prefix = IMailSettings.__identifier__ + "."
        key = prefix + "sender"
        del self.registry.records._values[key]
        del self.registry.records._fields[key]
        proxy2 = self.registry.forInterface(IMailSettings)
        self.assertIs(proxy1, proxy2)

    def test_forinterface_same_prefix_different_interface_not_shared(self):
        """Different interfaces with same prefix get separate proxies."""
        self._setRequest()
        proxy1 = self.registry.forInterface(
            IMailSettings, check=False, prefix="shared.prefix"
        )
        proxy2 = self.registry.forInterface(
            IMailPreferences, check=False, prefix="shared.prefix"
        )
        self.assertIsNot(proxy1, proxy2)
        self.assertTrue(IMailSettings.providedBy(proxy1))
        self.assertTrue(IMailPreferences.providedBy(proxy2))

    def test_forinterface_different_prefix_not_shared(self):
        """Different prefixes get separate cached proxies."""
        self._setRequest()
        self.registry.registerInterface(IMailSettings, prefix="alt.settings")
        proxy1 = self.registry.forInterface(IMailSettings)
        proxy2 = self.registry.forInterface(IMailSettings, prefix="alt.settings")
        self.assertIsNot(proxy1, proxy2)

    def test_forinterface_different_omit_not_shared(self):
        """Different omit tuples get separate cached proxies."""
        self._setRequest()
        proxy1 = self.registry.forInterface(IMailSettings)
        proxy2 = self.registry.forInterface(IMailSettings, omit=("sender",))
        self.assertIsNot(proxy1, proxy2)

    def test_forinterface_cache_isolation(self):
        """Different requests have independent proxy caches."""
        from zope.globalrequest import setRequest

        self._setRequest()
        proxy1 = self.registry.forInterface(IMailSettings)

        new_request = FakeRequest()
        setRequest(new_request)
        proxy2 = self.registry.forInterface(IMailSettings)
        self.assertIsNot(proxy1, proxy2)

    def test_forinterface_no_request_returns_new_each_time(self):
        """Without a request, each call returns a fresh proxy."""
        proxy1 = self.registry.forInterface(IMailSettings)
        proxy2 = self.registry.forInterface(IMailSettings)
        self.assertIsNot(proxy1, proxy2)


def test_suite():
    return unittest.TestSuite(
        [
            doctest.DocFileSuite(
                "registry.rst",
                package="plone.registry",
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                setUp=setUp,
                tearDown=testing.tearDown,
                checker=PolyglotOutputChecker(),
            ),
            doctest.DocFileSuite(
                "events.rst",
                package="plone.registry",
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                setUp=setUp,
                tearDown=testing.tearDown,
                checker=PolyglotOutputChecker(),
            ),
            doctest.DocFileSuite(
                "field.rst",
                package="plone.registry",
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                setUp=setUp,
                tearDown=testing.tearDown,
                checker=PolyglotOutputChecker(),
            ),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestBugs),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestMigration),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestRequestValueCache),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestForInterfaceCache),
        ]
    )
