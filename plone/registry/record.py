from persistent import Persistent

from zope.interface import implements, alsoProvides
from zope.component import queryAdapter

from zope.dottedname.resolve import resolve

from plone.registry.interfaces import IPersistentField
from plone.registry.interfaces import IRecord, IInterfaceAwareRecord

class Record(Persistent):
    """A record that is stored in the registry.
    """
    
    implements(IRecord)

    __name__ = u""
    __parent__ = None

    def __init__(self, field, value=None, interface=None, field_name=None):
        if not IPersistentField.providedBy(field):
            raise ValueError("Field is not persistent")

        if value is None:
            value = field.default

        field.__name__ = 'value'

        self.field = field
        self.value = value
        
        self.interface_name = None
        if interface is not None:
            alsoProvides(IInterfaceAwareRecord, self)
            self.interface_name = None
        self.field_name = field_name
    
    @property
    def interface(self):
        return resolve(self.interface_name)