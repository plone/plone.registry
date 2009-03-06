import zope.interface
import zope.component

import plone.registry.field

from zope.schema.interfaces import IField
from plone.registry import IPersistentField

@zope.component.implementer(IPersistentField)
@zope.component.adapter(IField)
def persistent_field_adapter(context):
    """Turn a non-persistent field into a persistent one
    """
    
    if IPersistentField.providedBy(context):
        return context
    
    # See if we have an equivalently-named field
    
    class_name = context.__class__.__name__
    persistent_class = getattr(plone.registry.field, class_name, None)
    if persistent_class is None:
        return None
    
    # Let it initialise itself from its sibling
    
    return persistent_class.fromSibling(context)