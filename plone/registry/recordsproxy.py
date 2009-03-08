from zope.interface import implements, alsoProvides
from plone.registry.interfaces import IRecordsProxy

_marker = object()

class RecordsProxy(object):
    """A proxy that maps an interface to a number of records
    """
    
    implements(IRecordsProxy)
    
    def __init__(self, registry, interface):
        
        # skip __setattr__
        self.__dict__['__interface__'] = interface
        self.__dict__['__registry__'] = registry
        self.__dict__['__prefix__'] = interface.__identifier__ + '.'
        
        alsoProvides(self, interface)
        
    def __getattr__(self, name):
        if name not in self.__interface__:
            raise AttributeError(name)
        value = self.__registry__.get(self.__prefix__ + name, _marker)
        if value is _marker:
            value = self.__interface__[name].missing_value
        return value
        
    def __setattr__(self, name, value):
        if name in self.__interface__:
            self.__registry__[self.__prefix__ + name] = value
        else:
            self.__dict__[name] = value