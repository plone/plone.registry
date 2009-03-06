from zope.interface import Interface
from zope.interface.interfaces import IInterface

from zope import schema

from zope.schema.interfaces import IField

class IPersistentField(IField):
    """A field that can be persistent along with a record.
    
    
    We provide our own implementation of the basic field types that are
    supported by the registry.
    """
    
    def fromSibling(sibling):
        """Create a persistent field form a non-persistent sibling field.
        
        This is a class method.
        """

class IRecord(Interface):
    """A record stored in the registry.
    """
    
    field = schema.Object(title=u"A field describing this record",
                          schema=IPersistentField)
    
    value = schema.Field(title=u"The value of this record",
                         description=u"Must be valid according to the record's field")

class IInterfaceAwareRecord(Interface):
    """A record will be marked with this interface if it knows which
    interface its field came from.
    """
    
    interface_name = schema.DottedName(title=u"Dotted name to interface")
    
    interface = schema.Object(title=u"Interface that provided the record",
                              description=u"May raise ImportError if the " \
                                            "interface is no longer available",
                              schema=IInterface)
    
    field_name = schema.ASCIILine(title=u"Name of the field in the original interface")

class IRecordsProxy(Interface):
    """This object is returned by IRegistry.by_interface(). It will be
    made to provide the relevant interface, i.e. it will have the
    attributes that the interface promises. Those attributes will be retrieved
    from or written to the underlying IRegistry.
    """

class IRegistry(Interface):
    """The configuration registry
    """
    
    def __getitem__(key):
        """Get the value under the given key. A record must have been
        installed for this key for this to be valid. Otherwise, a KeyError is
        raised.
        """

    def get(key, default=None):
        """Attempt to get the value under the given key. If it does not
        exist, return the given default.
        """

        
    def __setitem__(key, value):
        """Set the value under the given key. A record must have been
        installed for this key for this to be valid. Otherwise, a KeyError is
        raised. If value is not of a type that's allowed by the record, a
        ValidationError is raised.
        """
        
    def __contains__(key):
        """Determine if the registry contains a record for the given key.
        """
        
    records = schema.Dict(
            title=u"The records of the registry",
            key_type=schema.DottedName(
                    title=u"Name of the record",
                    description=u"By convention, this should include the "
                                 "package name and optionally an interface "
                                 "named, if the record can be described by a "
                                 "field in an interface (see also "
                                 "register_interface() below), e.g. "
                                 "my.package.interfaces.IMySettings.somefield.",
                ),
            value_type=schema.Object(
                    title=u"The record for this name",
                    schema=IRecord,
                ),
        )
        
    def for_interface(interface):
        """Get an IRecordsProxy for the given interface.
        """

    def register_interface(interface):
        """Create a set of records based on the given interface. For each
        schema field in the interface, a record will be inserted with a
        name like `${interface.__identifier__}.${field.__name__}`, and a
        value equal to default value of that field.
        """