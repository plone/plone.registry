from zope.interface import implements, alsoProvides
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import RequiredMissing, ISequence, IAbstractSet
from plone.registry.interfaces import IRecordsProxy
#from plone.registry import Record
from listmixin import ListMixin

from UserDict import DictMixin
import re

_marker = object()

class RecordsProxy(object):
    """A proxy that maps an interface to a number of records
    """
    
    implements(IRecordsProxy)
    
    def __init__(self, registry, schema, omitted=(), prefix=None, key_names={}):
        if prefix is None:
            prefix = schema.__identifier__ + '.'
        elif not prefix.endswith("."):
             prefix += '.'
        
        # skip __setattr__
        self.__dict__['__schema__'] = schema
        self.__dict__['__registry__'] = registry
        self.__dict__['__omitted__'] = omitted
        self.__dict__['__prefix__'] = prefix
        self.__dict__['__key_names__'] = key_names

        alsoProvides(self, schema)

    def __getattr__(self, name):
        if name not in self.__schema__:
            raise AttributeError(name)
        field = self.__schema__[name]
        if ISequence.providedBy(field):
            prefix = self.__prefix__ + name
            factory = None
            key_name = self.__key_names__.get(name,None)
            return RecordsProxyList(self.__registry__, field.value_type.schema, False, self.__omitted__, prefix, factory,
                                    key_name=key_name)
        elif IAbstractSet.providedBy(field):
            prefix = self.__prefix__ + name
            factory = None
            return RecordsProxyCollection(self.__registry__, field.value_type.schema, False, self.__omitted__, prefix, factory)
        else:
            value = self.__registry__.get(self.__prefix__ + name, _marker)
            if value is _marker:
                value = self.__schema__[name].missing_value
            return value

    def __setattr__(self, name, value):
        if name in self.__schema__:
            full_name = self.__prefix__ + name
            field = self.__schema__[name]
            if ISequence.providedBy(field):
                proxy = self.__getattr__(name)
                proxy[:] = value
            elif IAbstractSet.providedBy(field):
                proxy = self.__getattr__(name)
                proxy[:] = value
            else:
                if full_name not in self.__registry__:
                    raise AttributeError(name)
                self.__registry__[full_name] = value
        else:
            self.__dict__[name] = value

    def __repr__(self):
        return "<%s for %s>" % (self.__class__.__name__, self.__schema__.__identifier__)

class RecordsProxyCollection(DictMixin):
    """A proxy that maps a collection of RecordsProxy objects
    """

    _validkey = re.compile(r"([a-zA-Z][a-zA-Z0-9_]*)$").match

    # ord('.') == ord('/') - 1

    def __init__(self, registry, schema, check=True, omitted=(), prefix=None, factory=None):
        if prefix is None:
            prefix = schema.__identifier__

        if not prefix.endswith("/"):
             prefix += '/'

        self.registry = registry
        self.schema = schema
        self.check = check
        self.omitted = omitted
        self.prefix = prefix
        self.factory = factory

    def __getitem__(self, key):
        if self.has_key(key):
            prefix = self.prefix + key
            proxy = self.registry.forInterface(self.schema, self.check, self.omitted, prefix, self.factory)
            return proxy
        raise KeyError(key)

    def __iter__(self):
        min = self.prefix
        max = self.prefix[:-1] + '0'
        keys = self.registry.records.keys(min, max)
        len_prefix = len(self.prefix)
        last = None
        for name in keys:
            name = name[len_prefix:]
            key, extra = name.split('.', 1)
            if key != last:
                yield key
                last = key

    def keys(self):
        return list(iter(self))

    def _validate(self, key):
        if not isinstance(key, basestring) or not self._validkey(key):
            raise TypeError('expected a valid key (alphanumeric or underscore, starting with alpha)')
        return str(key)

    def has_key(self, key):
        key = self._validate(key)
        prefix = self.prefix + key
        names = self.registry.records.keys(prefix+'.', prefix+'/')
        return bool(names)

    def add(self, key):
        key = self._validate(key)
        prefix = self.prefix + key
        self.registry.registerInterface(self.schema, self.omitted, prefix)
        proxy = self.registry.forInterface(self.schema, False, self.omitted, prefix)
        return proxy

    def __setitem__(self, key, value):
        key = self._validate(key)
        data = {}
        for name, field in getFieldsInOrder(self.schema):
            if name in self.omitted or field.readonly:
                continue
            attr = getattr(value, name, _marker)
            if attr is not _marker:
                data[name] = attr
            elif field.required and self.check:
                raise RequiredMissing(name)

        proxy = self.add(key)
        for name, attr in data.items():
            setattr(proxy, name, attr)

    def setdefault(self, key, failobj=None):
        if not self.has_key(key):
            if failobj is None:
                self.add(key)
            else:
                self[key] = failobj
        return self[key]

    def __delitem__(self, key):
        if not self.has_key(key):
            raise KeyError(key) 
        prefix = self.prefix + key
        names = list(self.registry.records.keys(prefix+'.', prefix+'/'))
        for name in names:
            del self.registry.records[name]


class RecordsProxyList(ListMixin):
    """A proxy that represents a List of RecordsProxy objects.
        Two storage schemes are supported. A pure listing
        stored as prefix+"/i0001" where the number is the index.
        If your list has a field which can be used as a primary key
        you can pass they key_name in as an optional paramter. This will change
        the storage format where each entry is prefix+"/"+key_value which looks
        a lot nicer in the registry. Order is still
        kept in a special prefix+'.ordereddict_keys' entry.
    """

    def __init__(self, registry, schema, check=True, omitted=(), prefix=None, factory=None, key_name=None):
        self.map = RecordsProxyCollection(registry, schema, check, omitted, prefix, factory)
        self.key_name = key_name

        if key_name is not None:
            # will store as ordereddict with items stored using key_name's value and order kept in special keys list
            keys_key = prefix+'.ordereddict_keys'
            if registry.get(keys_key) is None:
                registry.records[keys_key] = Record(field.List(title=u"Keys of prefix"), [])
            self.keys = registry.records[keys_key]

    def _get_element(self, i):
        return self.map[self.genKey(i)]

    def _set_element(self, index, value):
        if self.key_name is not None:
            key = getattr(value, self.key_name)
            # first we have to remove the old value if it's being overwritten
            oldkey = self.keys.value[index]
            if key != oldkey and oldkey is not None:
                del self.map[oldkey]
            self.keys.value[index] = key
        self.map[self.genKey(index)] = value

    def __len__(self):
        if self.key_name is None:
            return len(self.map)
        else:
            return len(self.keys.value)

    def _resize_region(self, start, end, new_size):
        #move everything along one
        offset = new_size - (end - start)

        # remove any additional at the end
        for i in range(len(self.map)+offset, len(self.map)):
            del self.map[self.genKey(i)]

        if self.key_name is None:
            if offset > 0:
                moves = range(end-1, start, -1)
            else:
                moves = range(start, end, +1)
            for i in moves:
                if i < len(self.map):
                    self.map[self.genKey(i+offset)] = self.map[self.genKey(i)]
        else:
            self.keys.value = self.keys.value[:start] + [None for i in range(new_size)] + self.keys.value[end:]

    def genKey(self, index):
        if self.key_name is None:
            index_prefix = "i"
            return "%s%05d" %(index_prefix, index)
        else:
            return self.keys.value[index]

