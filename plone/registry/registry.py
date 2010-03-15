from persistent import Persistent
from BTrees.OOBTree import OOBTree

from zope.interface import implements
from zope.component import queryAdapter
from zope.event import notify

from zope.schema import getFieldNames, getFieldsInOrder
from zope.schema.interfaces import InvalidDottedName
from zope.schema._field import _isdotted

from plone.registry.interfaces import IRegistry, IRecord, IPersistentField
from plone.registry.record import Record
from plone.registry.recordsproxy import RecordsProxy
from plone.registry.events import RecordAddedEvent, RecordRemovedEvent

class Registry(Persistent):
    """The persistent registry
    """
    
    implements(IRegistry)
    
    def __init__(self):
        self._records = Records(self)
    
    # Basic value access API
    
    def __getitem__(self, name):
        return self.records[name].value
    
    def get(self, name, default=None):
        record = self.records.get(name, None)
        if record is None:
            return default
        return record.value
    
    def __setitem__(self, name, value):
        self.records[name].value = value
    
    def __contains__(self, name):
        return name in self.records
    
    # Records - make this a property so that it's readonly
    
    @property
    def records(self):
        return self._records
    
    # Schema interface API
    
    def forInterface(self, interface, check=True, omit=()):
        prefix = interface.__identifier__ + '.'
        if check:
            for name in getFieldNames(interface):
                if name not in omit and prefix + name not in self.records:
                    raise KeyError("Interface `%s` defines a field `%s`, "
                                   "for which there is no record." % (interface.__identifier__, name))
        
        return RecordsProxy(self, interface, omitted=omit)

    def registerInterface(self, interface, omit=(), prefix=None):
        if prefix is None:
            prefix = interface.__identifier__
        
        if not prefix.endswith("."):
             prefix += '.'
        
        for name, field in getFieldsInOrder(interface):
            if name in omit or field.readonly:
                continue
            record_name = prefix + name
            persistent_field = queryAdapter(field, IPersistentField)
            if persistent_field is None:
                raise TypeError("There is no persistent field equivalent for "
                                "the field `%s` of type `%s`." % (name, field.__class__.__name__))
            
            value = persistent_field.default
            
            # Attempt to retain the exisiting value
            if record_name in self.records:
                existing_record = self.records[record_name]
                value = existing_record.value
                bound_field = persistent_field.bind(existing_record)
                try:
                    bound_field.validate(value)
                except:
                    value = persistent_field.default
            
            self.records[record_name] = Record(persistent_field, value, 
                                               interface=interface, fieldName=name)

class Records(Persistent):
    """The records stored in the registry
    """
    
    __parent__ = None
    
    def __init__(self, parent):
        self.__parent__ = parent
        self.data = OOBTree()

    def __setitem__(self, name, record):
        if not _isdotted(name):
            raise InvalidDottedName(record)
        if not IRecord.providedBy(record):
            raise ValueError("Value must be a record")
        if not IPersistentField.providedBy(record.field):
            raise ValueError("The record's field must be an IPersistentField.")
        
        record.__name__ = name
        record.__parent__ = self.__parent__
        self.data[name] = record
        notify(RecordAddedEvent(record))
    
    def __delitem__(self, name):
        record = self[name]
        del self.data[name]
        notify(RecordRemovedEvent(record))

    # Unfortunately, you can't just subclass an OOBTree if you want to
    # persist it...

    def __getitem__(self, name):
        return self.data.__getitem__(name)
    
    def get(self, name, default=None):
        return self.data.get(name, default)
    
    def __nonzero__(self):
        return self.data.__nonzero__()
    
    def __len__(self):
        return self.data.__len__()
        
    def __iter__(self):
        return self.data.__iter__()
    
    def __getslice__(self, index1, index2):
        return self.data.__getslice__(index1, index2)
        
    def has_key(self, name):
        return self.data.has_key(name)
        
    def __contains__(self, name):
        return self.data.__contains__(name)
        
    def keys(self, min=None, max=None, excludemin=False, excludemax=False):
        return self.data.keys(min, max, excludemin, excludemax)
        
    def maxKey(self, key=None):
        return self.data.maxKey(key)
        
    def minKey(self, key=None):
        return self.data.minKey(key)
        
    def values(self, min=None, max=None, excludemin=False, excludemax=False):
        return self.data.values(min, max, excludemin, excludemax)
        
    def items(self, min=None, max=None, excludemin=False, excludemax=False):
        return self.data.items(min, max, excludemin, excludemax)
    
    def update(self, collection):
        self.data.update(collection)
        
    def byValue(self, minValue):
        self.data.byValue(minValue)
        
    def setdefault(self, key, d):
        return self.data.setdefault(key, d)
        
    def pop(self, key, d):
        return self.data.pop(key, d)
        
    def insert(self, key, value):
        self.data.insert(key, value)
        
    def difference(self, c1, c2):
        return self.data.difference(c1, c2)
        
    def union(self, c1, c2):
        return self.data.union(c1, c2)
    
    def intersection(self, c1, c2):
        return self.data.intersection(c1, c2)
    
    def clear(self):
        self.data.clear()