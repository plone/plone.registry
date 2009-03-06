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

class PersistentField(persistent.Persistent, zope.schema.Field):
    """Base class for persistent field definitions.
    """
    
    def __init__(self, title=u'', description=u'', __name__='',
                 required=True, readonly=False, constraint=None, default=None,
                 missing_value=_missing_value_marker):
        
        # We need to override the constructor, because we don't want this to
        # change the Field.order class variable
        
        __doc__ = ''
        if title:
            if description:
                __doc__ = "%s\n\n%s" % (title, description)
            else:
                __doc__ = title
        elif description:
            __doc__ = description

        zope.interface.Attribute.__init__(self, __name__, __doc__)
        
        self.title = title
        self.description = description
        self.required = required
        self.readonly = readonly
        if constraint is not None:
            self.constraint = constraint
        self.default = default

        self.order = -1

        if missing_value is not _missing_value_marker:
            self.missing_value = missing_value
    
    @classmethod
    def fromSibling(cls, sibling):
        if not issubclass(cls, sibling.__class__):
            raise ValueError("Can only clone a field of an equivalent type.")
        
        inst = cls.__new__(cls)
        ignored = {'order': -1}
        import pdb; pdb.set_trace( )
        for k, v in sibling.__dict__.items():
            if k in ignored:
                v = ignored[k]
            setattr(inst, k, v)
            
        return inst
    
# class PersistentCollectionField(PersistentField, zope.schema._field.AbstractCollection):
#     pass
#     
#     # TODO: make sure value_type is persistent too

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
    
# class Tuple(PersistentCollectionField, zope.schema.Tuplie):
#     pass
#     
# class List(PersistentCollectionField, zope.schema.List):
#     pass
# 
# class Set(PersistentCollectionField, zope.schema.Set):
#     pass
#     
# class FrozenSet(PersistentCollectionField, zope.schema.FrozenSet):
#     pass

class Password(PersistentField, zope.schema.Password):
    pass

# class Dict(PersistentField, zope.schema.Dict):
#     pass
#     
#     # TODO: Ensure key_type and value_type are persistent
    
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
