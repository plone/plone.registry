from zope.interface import implements

from plone.registry.interfaces import IRecordEvent
from plone.registry.interfaces import IRecordAddedEvent
from plone.registry.interfaces import IRecordRemovedEvent
from plone.registry.interfaces import IRecordModifiedEvent

class RecordEvent(object):
    implements(IRecordEvent)

    def __init__(self, record):
        self.record = record

    def __repr__(self):
        return "<%s for %s>" % (self.__class__.__name__, self.record.__name__)

class RecordAddedEvent(RecordEvent):
    implements(IRecordAddedEvent)

class RecordRemovedEvent(RecordEvent):
    implements(IRecordRemovedEvent)

class RecordModifiedEvent(RecordEvent):
    implements(IRecordModifiedEvent)
    
    def __init__(self, record, old_value, new_value):
        super(RecordModifiedEvent, self).__init__(record)
        self.old_value = old_value
        self.new_value = new_value