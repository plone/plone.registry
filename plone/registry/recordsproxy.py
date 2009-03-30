from zope.interface import implements, alsoProvides
from plone.registry.interfaces import IRecordsProxy

_marker = object()

class RecordsProxy(object):
    """A proxy that maps an interface to a number of records
    """
    
    implements(IRecordsProxy)
    
    def __init__(self, registry, schema, omitted=()):
        
        # skip __setattr__
        self.__dict__['__schema__'] = schema
        self.__dict__['__registry__'] = registry
        self.__dict__['__omitted__'] = omitted
        self.__dict__['__prefix__'] = schema.__identifier__ + '.'
        
        alsoProvides(self, schema)
        
    def __getattr__(self, name):
        if name not in self.__schema__:
            raise AttributeError(name)
        value = self.__registry__.get(self.__prefix__ + name, _marker)
        if value is _marker:
            value = self.__schema__[name].missing_value
        return value
        
    def __setattr__(self, name, value):
        if name in self.__schema__:
            full_name = self.__prefix__ + name
            if full_name not in self.__registry__:
                raise AttributeError(name)
            self.__registry__[full_name] = value
        else:
            self.__dict__[name] = value
    
    def __repr__(self):
        return "<RecordsProxy for %s>" % self.__schema__.__identifier__