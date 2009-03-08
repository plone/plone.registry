from persistent import Persistent

from zope.interface import implements, alsoProvides

from zope.dottedname.resolve import resolve

from plone.registry.interfaces import IPersistentField
from plone.registry.interfaces import IRecord, IInterfaceAwareRecord

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
        inst.__dict__[self._name] = value

class Record(Persistent):
    """A record that is stored in the registry.
    """
    
    implements(IRecord)

    __name__ = u""
    __parent__ = None

    _value = None

    field = None
    value = FieldValidatedProperty('value', None)

    def __init__(self, field, value=None, interface=None, field_name=None):
        if not IPersistentField.providedBy(field):
            raise ValueError("Field is not persistent")

        if value is None:
            value = field.default

        # This lets field.set() work on the record
        field.__name__ = 'value'

        self.field = field
        self.value = value
        
        self.interface_name = None
        if interface is not None:
            alsoProvides(self, IInterfaceAwareRecord)
            self.interface_name = interface.__identifier__
        self.field_name = field_name
    
    @property
    def interface(self):
        try:
            return resolve(self.interface_name)
        except ImportError:
            return None