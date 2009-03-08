from persistent import Persistent
from BTrees.OOBTree import OOBTree

from zope.interface import implements
from zope.component import queryAdapter

from zope.schema import getFieldNames, getFieldsInOrder
from zope.schema.interfaces import InvalidDottedName
from zope.schema._field import _isdotted

from plone.registry.interfaces import IRegistry, IRecord, IPersistentField
from plone.registry.record import Record
from plone.registry.recordsproxy import RecordsProxy

class Records(OOBTree):
    """The records stored in the registry
    """
    
    def __setitem__(self, name, record):
        if not _isdotted(name):
            raise InvalidDottedName(record)
        if not IRecord.providedBy(record):
            raise ValueError("Value must be a record")
        if not IPersistentField.providedBy(record.field):
            raise ValueError("The record's field must be an IPersistentField.")
        
        record.__name__ = name
        record.__parent__ = self.__parent__
        super(Records, self).__setitem__(name, record)
        
class Registry(Persistent):
    """The persistent registry
    """
    
    implements(IRegistry)
    
    def __init__(self):
        self._records = Records()
        self._records.__parent__ = self
    
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
    
    def for_interface(self, interface, check=True, omit=()):
        prefix = interface.__identifier__ + '.'
        if check:
            for name in getFieldNames(interface):
                if name not in omit and prefix + name not in self.records:
                    raise KeyError("Interface `%s` defines a field `%s`, "
                                   "for which there is no record." % (interface.__identifier__, name))
        
        return RecordsProxy(self, interface, omitted=omit)

    def register_interface(self, interface, omit=()):
        prefix = interface.__identifier__ + '.'
        for name, field in getFieldsInOrder(interface):
            if name in omit or field.readonly:
                continue
            record_name = prefix + name
            persistent_field = queryAdapter(field, IPersistentField)
            if persistent_field is None:
                raise TypeError("There is no persistent field equivalent for "
                                "the field `%s` of type `%s`." % (name, field.__class__.__name__))
            value = persistent_field.default
            self.records[record_name] = Record(persistent_field, value, 
                                               interface=interface, field_name=name)