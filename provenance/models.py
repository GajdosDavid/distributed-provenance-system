from neomodel import (StructuredRel, StructuredNode, UniqueIdProperty,
                      StringProperty, JSONProperty, DateTimeFormatProperty, RelationshipTo, RelationshipFrom)


class BaseProvRelationship(StructuredRel):
    identifier = StringProperty()
    attributes = JSONProperty()


class WasGeneratedBy(BaseProvRelationship):
    time = DateTimeFormatProperty()


class Usage(BaseProvRelationship):
    time = DateTimeFormatProperty()


class WasInformedBy(BaseProvRelationship):
    pass

class WasStartedBy(BaseProvRelationship):



class BundledIn(BaseProvRelationship):
    time = DateTimeFormatProperty()


class BaseProvNode(StructuredNode):
    uid = UniqueIdProperty()
    identifier = StringProperty(required=True)
    attributes = JSONProperty()

    bundled_in = RelationshipTo('Bundle', 'BUNDLED_IN', model=BundledIn)


class Entity(BaseProvNode):
    was_generated_by = RelationshipTo('Activity', 'WAS_GENERATED_BY', model=WasGeneratedBy)

    used = RelationshipFrom('Activity', 'USED', model=Usage)


class Activity(BaseProvNode):
    start_time = DateTimeFormatProperty()
    end_time = DateTimeFormatProperty()

    used = RelationshipTo('Entity', 'USED', model=Usage)
    was_informed_by = RelationshipTo('Activity', 'WAS_INFORMED_BY', model=WasGeneratedBy)

    was_generated_by = RelationshipFrom('Entity', 'WAS_GENERATED_BY', model=WasGeneratedBy)



class Agent(BaseProvNode):
    pass


class Bundle(BaseProvNode):
    pass
