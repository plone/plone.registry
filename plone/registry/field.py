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

    def __set__(self, inst, value):
        raise ValueError(u"Persistent fields does not support setting the %s property" % self._name)

class StubbornProperty(object):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def __set__(self, inst, value):
        if value != inst.missing_value:
            value = self._value
        inst.__dict__[self._name] = value

class PersistentFieldProperty(object):
    
    def __init__(self, name):
        self._name = name
        
    def __set__(self, inst, value):
        if value != inst.missing_value:
            if not IPersistentField.providedBy(value):
                raise ValueError(u"The property %s may only contain persistent fields." % self._name)
        inst.__dict__[self._name] = value

class PersistentField(persistent.Persistent):
    """Base class for persistent field definitions.
    """
    
    zope.interface.implements(IPersistentField)
    
    _ignored_properties = set(['order', 'constraint'])
    
    # Persistent fields do not have an order
    order = StubbornProperty('order', -1)
    
    # We don't allow setting a custom constraint, as this would introduce a
    # dependency on a symbol such as a function that may go away
    constraint = DisallowedProperty()
    
    @classmethod
    def fromSibling(cls, sibling):
        if not issubclass(cls, sibling.__class__):
            raise ValueError("Can only clone a field of an equivalent type.")
        
        # TODO: Need to test for Stubborn, Disallowed and PersistentField properties
        
        inst = cls.__new__(cls)
        
        sibling_dict = dict([(k,v) for k,v in sibling.__dict__.items() 
                                if k not in cls._ignored_properties])

        inst.__dict__.update(sibling_dict)
        return inst

class PersistentCollectionField(PersistentField, zope.schema._field.AbstractCollection):
    """Ensure that value_type is a persistent field
    """
    
    value_type = PersistentFieldProperty('value_type')
    
    
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
    
    key_type = PersistentFieldProperty('key_type')
    value_type = PersistentFieldProperty('value_type')
    
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
