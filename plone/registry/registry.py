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
            
            persistent_field.interfaceName = interface.__identifier__
            persistent_field.fieldName = name
            
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
            
            self.records[record_name] = Record(persistent_field, value, _validate=False)

class Records(object):
    """The records stored in the registry
    """
    
    __parent__ = None
    
    def __init__(self, parent):
        self.__parent__ = parent
        
        self.fields = OOBTree()
        self.data = OOBTree()

    def __setitem__(self, name, record):
        if not _isdotted(name):
            raise InvalidDottedName(record)
        if not IRecord.providedBy(record):
            raise ValueError("Value must be a record")
        if not IPersistentField.providedBy(record.field):
            raise ValueError("The record's field must be an IPersistentField.")
        
        self.fields[name] = record.field
        self.data[name] = record.value
        
        record.__name__ = name
        record.__parent__ = self.__parent__
        
        notify(RecordAddedEvent(record))
    
    def __delitem__(self, name):
        record = self[name]
        
        # unbind the record so that it won't attempt to look up values from
        # the registry anymore
        record.__parent__ = None
        
        del self.fields[name]
        del self.data[name]
        
        notify(RecordRemovedEvent(record))
    
    # Basic dict API
    
    def __getitem__(self, name):
        
        field = self.fields[name]
        value = self.data[name]
        
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
        return self.data.__nonzero__()
    
    def __len__(self):
        return self.data.__len__()
        
    def __iter__(self):
        return self.data.__iter__()
    
    def has_key(self, name):
        return self.data.has_key(name)
        
    def __contains__(self, name):
        return self.data.__contains__(name)
        
    def keys(self):
        return self.data.keys()
        
    def maxKey(self, key=None):
        return self.data.maxKey(key)
        
    def minKey(self, key=None):
        return self.data.minKey(key)
        
    def values(self):
        return [self[name] for name in self.keys()]
        
    def items(self):
        return [(name, self[name],) for name in self.keys()]
    
    def setdefault(self, key, value):
        if key not in self:
            self[key] = value
        return self[key]

    def clear(self):
        self.fields.clear()
        self.data.clear()
