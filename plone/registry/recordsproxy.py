from zope.interface import implements, alsoProvides
from plone.registry.interfaces import IRecordsProxy

_marker = object()

class RecordsProxy(object):
    """A proxy that maps an interface to a number of records
    """
    
    implements(IRecordsProxy)
    
    def __init__(self, registry, interface):
        self.__registry = registry
        self.__prefix = interface.__identifier__ + '.'
        self.__interface = interface
        alsoProvides(self, interface)
        
    def __getattr__(self, name):
        if name not in self.__interface:
            raise AttributeError(name)
        value = self.__registry.get(self.__prefix + name, _marker)
        if value is _marker:
            value = self.__interface[name].default
        return value
        
    def __setattr__(self, name, value):
        if name not in self.__interface:
            raise AttributeError(name)
        try:
            self.__registry[name] = value
        except KeyError:
            raise AttributeError(name)