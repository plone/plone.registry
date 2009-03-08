"""This module defines persistent versions of various fields.

The idea is that when a record is created, we copy relevant field properties
from the transient schema field from zope.schema, into the corresponding
persistent field. Note all field types are supported, but the common types
are.
"""

import persistent

import zope.interface

import zope.schema
import zope.schema._field

_missing_value_marker = object()

from plone.registry.interfaces import IPersistentField

class DisallowedProperty(object):
    """A property that may not be set on an instance. It may still be set
    defined in a base class.
    """

    uses = []
    
    def __init__(self, name):
        self.name = name
        DisallowedProperty.uses.append(name)
    
    def __get__(self, inst, type_=None):
        # look for the object in bases
        if type_ is not None:
            for c in type_.__mro__:
                if self.name in c.__dict__ and not \
                        isinstance(c.__dict__[self.name], DisallowedProperty):
                    function = c.__dict__[self.name]
                    return function.__get__(inst, type_)
        raise AttributeError(self.name)
        
    def __set__(self, inst, value):
        raise ValueError(u"Persistent fields does not support setting the `%s` property" % self._name)

class StubbornProperty(object):
    """A property that stays stubbornly at a single, pre-defined value.
    """

    uses = []

    def __init__(self, name, value):
        StubbornProperty.uses.append(name)
        self._name = name
        self._value = value

    def __set__(self, inst, value):
        pass
        
    def __get__(self):
        return self._value

class InterfaceConstrainedProperty(object):
    """A property that may only contain values providing a certain interface.
    """
    
    uses = []
    
    def __init__(self, name, interface):
        InterfaceConstrainedProperty.uses.append((name, interface))
        self._name = name
        self._interface = interface
        
    def __set__(self, inst, value):
        if value != inst.missing_value:
            if not self._interface.providedBy(value):
                raise ValueError(u"The property `%s` may only contain objects providing `%s`." % 
                                    (self._name, self._interface.__identifier__,))
        inst.__dict__[self._name] = value

class PersistentField(persistent.Persistent):
    """Base class for persistent field definitions.
    """
    
    zope.interface.implements(IPersistentField)
    
    # Persistent fields do not have an order
    order = StubbornProperty('order', -1)
    
    # We don't allow setting a custom constraint, as this would introduce a
    # dependency on a symbol such as a function that may go away
    constraint = DisallowedProperty('constraint')
    
    @classmethod
    def fromSibling(cls, sibling):
        if not issubclass(cls, sibling.__class__):
            raise ValueError("Can only clone a field of an equivalent type.")
        
        ignored = list(DisallowedProperty.uses + StubbornProperty.uses)
        persistent = list(InterfaceConstrainedProperty.uses)
        
        inst = cls.__new__(cls)
        
        sibling_dict = dict([(k,v) for k,v in sibling.__dict__.items() 
                                if k not in ignored])

        for k in persistent:
            v = sibling_dict.get(k, None)
            if v is not None and v != sibling.missing_value:
                v = IPersistentField(v, None)
                if v is None:
                    raise ValueError(u"The property %s may only contain persistable fields." % k)

        inst.__dict__.update(sibling_dict)
        return inst

class PersistentCollectionField(PersistentField, zope.schema._field.AbstractCollection):
    """Ensure that value_type is a persistent field
    """
    
    value_type = InterfaceConstrainedProperty('value_type', IPersistentField)
    
class Bytes(PersistentField, zope.schema.Bytes):
    pass

class BytesLine(PersistentField, zope.schema.BytesLine):
    pass

class ASCII(PersistentField, zope.schema.ASCII):
    pass

class ASCIILine(PersistentField, zope.schema.ASCIILine):
    pass

class Text(PersistentField, zope.schema.Text):
    pass

class TextLine(PersistentField, zope.schema.TextLine):
    pass
    
class Bool(PersistentField, zope.schema.Bool):
    pass

class Int(PersistentField, zope.schema.Int):
    pass
    
class Tuple(PersistentCollectionField, zope.schema.Tuple):
    pass
    
class List(PersistentCollectionField, zope.schema.List):
    pass

class Set(PersistentCollectionField, zope.schema.Set):
    pass
    
class FrozenSet(PersistentCollectionField, zope.schema.FrozenSet):
    pass

class Password(PersistentField, zope.schema.Password):
    pass

class Dict(PersistentField, zope.schema.Dict):
    
    key_type = InterfaceConstrainedProperty('key_type', IPersistentField)
    value_type = InterfaceConstrainedProperty('value_type', IPersistentField)
    
class Datetime(PersistentField, zope.schema.Datetime):
    pass
    
class Date(PersistentField, zope.schema.Date):
    pass
    
class Timedelta(PersistentField, zope.schema.Timedelta):
    pass

class SourceText(PersistentField, zope.schema.SourceText):
    pass
    
class URI(PersistentField, zope.schema.URI):
    pass
    
class Id(PersistentField, zope.schema.Id):
    pass

class DottedName(PersistentField, zope.schema.DottedName):
    pass
    
# class Choice(PersistentField, zope.schema.Choice):
#     pass
#     
#     # TODO: We can only support sources based on named vocabularies
