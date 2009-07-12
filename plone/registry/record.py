from persistent import Persistent

from zope.interface import implements, alsoProvides
from zope.event import notify

from zope.dottedname.resolve import resolve

from plone.registry.interfaces import IPersistentField
from plone.registry.interfaces import IRecord, IInterfaceAwareRecord

from plone.registry.events import RecordModifiedEvent

class FieldValidatedProperty(object):
    
    def __init__(self, name, initial_value):
        self._name = name
        self._initial_value = initial_value
        
    def __get__(self, inst, type_=None):
        return inst.__dict__.get(self._name, self._initial_value)
    
    def __set__(self, inst, value):
        if inst.field is None:
            raise ValueError("The record's field must be set before its value")
        
        field = inst.field.bind(inst)
        if value != field.missing_value:
            field.validate(value)
        
        oldValue = self.__get__(inst)
        inst.__dict__[self._name] = value
        
        notify(RecordModifiedEvent(inst, oldValue, value))

_marker = object()

class Record(Persistent):
    """A record that is stored in the registry.
    """
    
    implements(IRecord)

    __name__ = u""
    __parent__ = None

    field = None
    value = FieldValidatedProperty('value', None)

    def __init__(self, field, value=_marker, interface=None, fieldName=None):
        if not IPersistentField.providedBy(field):
            raise ValueError("Field is not persistent")

        # This lets field.set() work on the record
        field.__name__ = 'value'

        self.field = field
        
        if value is _marker:
            value = field.default
        else:
            bound_field = field.bind(self)
            if value != bound_field.missing_value:
                bound_field.validate(value)
        
        # Bypass event notification
        self.__dict__['value'] = value
        
        self.interfaceName = None
        if interface is not None:
            alsoProvides(self, IInterfaceAwareRecord)
            self.interfaceName = interface.__identifier__
        self.fieldName = fieldName
    
    @property
    def interface(self):
        try:
            return resolve(self.interfaceName)
        except ImportError:
            return None
    
    def __repr__(self):
        return "<Record %s>" % self.__name__