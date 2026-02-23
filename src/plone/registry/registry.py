from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from plone.registry.events import RecordAddedEvent
from plone.registry.events import RecordRemovedEvent
from plone.registry.fieldref import FieldRef
from plone.registry.interfaces import IFieldRef
from plone.registry.interfaces import InvalidRegistryKey
from plone.registry.interfaces import IPersistentField
from plone.registry.interfaces import IRecord
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.registry.recordsproxy import RecordsProxy
from plone.registry.recordsproxy import RecordsProxyCollection
from zope.component import queryAdapter
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema import getFieldNames
from zope.schema import getFieldsInOrder

import re
import warnings


_CACHE_MARKER = object()


def _get_request_cache(context):
    """Return the per-request, per-registry value cache dict, or None.

    Uses ``request.other`` directly (the dict Zope's HTTPRequest clears
    at end-of-request).  Returns None when ``other`` is not available
    (e.g. zope.publisher TestRequest or dict-based test stubs).
    """
    request = getRequest()
    if request is None:
        return None
    other = getattr(request, "other", None)
    if other is None:
        return None
    all_caches = other.get("_plone_registry_cache")
    if all_caches is None:
        all_caches = {}
        other["_plone_registry_cache"] = all_caches
    registry_id = id(aq_base(context))
    try:
        return all_caches[registry_id]
    except KeyError:
        cache = {}
        all_caches[registry_id] = cache
        return cache


@implementer(IRegistry)
class Registry(Persistent):
    """The persistent registry"""

    def __init__(self):
        self._records = _Records(self)

    # Basic value access API

    def __getitem__(self, name):
        cache = _get_request_cache(self)
        if cache is not None:
            value = cache.get(name, _CACHE_MARKER)
            if value is not _CACHE_MARKER:
                return value
        value = self.records._values[name]
        if cache is not None:
            cache[name] = value
        return value

    def get(self, name, default=None):
        cache = _get_request_cache(self)
        if cache is not None:
            value = cache.get(name, _CACHE_MARKER)
            if value is not _CACHE_MARKER:
                return value
        value = self.records._values.get(name, _CACHE_MARKER)
        if value is _CACHE_MARKER:
            return default
        if cache is not None:
            cache[name] = value
        return value

    def __setitem__(self, name, value):
        # make sure we get the Record class' validation
        self.records[name].value = value
        cache = _get_request_cache(self)
        if cache is not None:
            cache[name] = value

    def __contains__(self, name):
        cache = _get_request_cache(self)
        if cache is not None and name in cache:
            return True
        return name in self.records._values

    # Records - make this a property so that it's readonly

    @property
    def records(self):
        # XXX: On-the-fly migration
        if isinstance(self._records, Records):
            self._migrateRecords()
        return self._records

    # Schema interface API

    def forInterface(self, interface, check=True, omit=(), prefix=None, factory=None):
        if prefix is None:
            prefix = interface.__identifier__

        if not prefix.endswith("."):
            prefix += "."

        cache = _get_request_cache(self)
        cache_key = ("__proxy__", interface.__identifier__, prefix, omit)
        if cache is not None:
            proxy = cache.get(cache_key)
            if proxy is not None:
                return proxy

        if check:
            for name in getFieldNames(interface):
                if name not in omit and prefix + name not in self:
                    raise KeyError(
                        "Interface `{}` defines a field `{}`, for which "
                        "there is no record.".format(interface.__identifier__, name)
                    )

        if factory is None:
            factory = RecordsProxy

        proxy = factory(self, interface, omitted=omit, prefix=prefix)

        if cache is not None:
            cache[cache_key] = proxy

        return proxy

    def registerInterface(self, interface, omit=(), prefix=None):
        if prefix is None:
            prefix = interface.__identifier__

        if not prefix.endswith("."):
            prefix += "."

        for name, field in getFieldsInOrder(interface):
            if name in omit or field.readonly:
                continue
            record_name = prefix + name
            persistent_field = queryAdapter(field, IPersistentField)
            if persistent_field is None:
                raise TypeError(
                    "There is no persistent field equivalent for the field "
                    "`{}` of type `{}`.".format(name, field.__class__.__name__)
                )

            persistent_field.interfaceName = interface.__identifier__
            persistent_field.fieldName = name

            value = persistent_field.default

            # Attempt to retain the existing value
            if record_name in self.records:
                existing_record = self.records[record_name]
                value = existing_record.value
                bound_field = persistent_field.bind(existing_record)
                try:
                    bound_field.validate(value)
                except Exception:
                    value = persistent_field.default

            self.records[record_name] = Record(persistent_field, value, _validate=False)

    def collectionOfInterface(
        self, interface, check=True, omit=(), prefix=None, factory=None
    ):
        return RecordsProxyCollection(self, interface, check, omit, prefix, factory)

    # BBB

    def _migrateRecords(self):
        """BBB: Migrate from the old Records structure to the new. This is
        done the first time the "old" structure is accessed.
        """
        records = _Records(self)

        oldData = getattr(self._records, "data", None)
        if oldData is not None:
            for name, oldRecord in oldData.iteritems():
                oldRecord._p_activate()
                if "field" in oldRecord.__dict__ and "value" in oldRecord.__dict__:
                    records._fields[name] = oldRecord.__dict__["field"]
                    records._values[name] = oldRecord.__dict__["value"]

        self._records = records


class _Records:
    """The records stored in the registry. This implements dict-like access
    to records, where as the Registry object implements dict-like read-only
    access to values.
    """

    __parent__ = None

    # Similar to zope.schema._field._isdotted, but allows up to one '/'
    _validkey = re.compile(
        r"([a-zA-Z][a-zA-Z0-9_-]*)((?:\.[a-zA-Z0-9][a-zA-Z0-9_-]*)*)"
        r"([/][a-zA-Z0-9][a-zA-Z0-9_-]*)?((?:\.[a-zA-Z0-9][a-zA-Z0-9_-]*)*)$"
    ).match

    def __init__(self, parent):
        self.__parent__ = parent

        self._fields = OOBTree()
        self._values = OOBTree()

    def _invalidate_cache(self):
        cache = _get_request_cache(self.__parent__)
        if cache is not None:
            cache.clear()

    def __setitem__(self, name, record):
        if not self._validkey(name):
            raise InvalidRegistryKey(record)
        if not IRecord.providedBy(record):
            raise ValueError("Value must be a record")

        self._setField(name, record.field)
        self._values[name] = record.value
        self._invalidate_cache()

        record.__name__ = name
        record.__parent__ = self.__parent__

        notify(RecordAddedEvent(record))

    def __delitem__(self, name):
        record = self[name]

        # unbind the record so that it won't attempt to look up values from
        # the registry anymore
        record.__parent__ = None

        del self._fields[name]
        del self._values[name]
        self._invalidate_cache()

        notify(RecordRemovedEvent(record))

    def __getitem__(self, name):
        field = self._getField(name)
        value = self._values[name]

        record = Record(field, value, _validate=False)
        record.__name__ = name
        record.__parent__ = self.__parent__

        return record

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def __nonzero__(self):
        return self._values.__nonzero__()

    def __len__(self):
        return self._values.__len__()

    def __iter__(self):
        return self._values.__iter__()

    def has_key(self, name):
        return self._values.__contains__(name)

    def __contains__(self, name):
        return self._values.__contains__(name)

    def keys(self, min=None, max=None):
        return self._values.keys(min, max)

    def maxKey(self, key=None):
        return self._values.maxKey(key)

    def minKey(self, key=None):
        return self._values.minKey(key)

    def values(self, min=None, max=None):
        return [self[name] for name in self.keys(min, max)]

    def items(self, min=None, max=None):
        return [(name, self[name]) for name in self.keys(min, max)]

    def setdefault(self, key, value):
        if key not in self:
            self[key] = value
        return self[key]

    def clear(self):
        self._fields.clear()
        self._values.clear()
        self._invalidate_cache()

    # Helper methods

    def _getField(self, name):
        field = self._fields[name]

        # Handle field reference pointers
        if isinstance(field, str):
            recordName = field
            while isinstance(field, str):
                recordName = field
                field = self._fields[recordName]
            field = FieldRef(recordName, field)

        return field

    def _setField(self, name, field):
        if not IPersistentField.providedBy(field):
            raise ValueError("The record's field must be an IPersistentField.")
        if IFieldRef.providedBy(field):
            if field.recordName not in self._fields:
                raise ValueError("Field reference points to non-existent record")
            self._fields[name] = field.recordName  # a pointer, of sorts
        else:
            field.__name__ = "value"
            self._fields[name] = field


class Records(_Records, Persistent):
    """BBB: This used to be the class for the _records attribute of the
    registry. Having this be a Persistent object was always a bad idea. We
    keep it here so that we can migrate to the new structure, but it should
    no longer be used.
    """

    def __init__(self, parent):
        warnings.warn(
            "The Records persistent class is deprecated and should not be " "used.",
            DeprecationWarning,
        )
        super().__init__(parent)
