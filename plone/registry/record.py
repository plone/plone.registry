from zope.interface import implements
from persistent import Persistent

from plone.registry.interfaces import IPersistentField, IRecord

class Record(Persistent):
    """A record that is stored in the registry.
    """
    
    implements(IRecord)

    def __init__(self, field, value=None):
        if not IPersistentField.providedBy(field):
            raise ValueError("Records can only contain persistent fields.")

        if value is None:
            value = field.default

        field.__name__ = 'value'

        self.field = field
        self.value = value