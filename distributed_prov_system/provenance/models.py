from neomodel import (StructuredRel, StructuredNode, StringProperty,
                      JSONProperty, DateTimeFormatProperty, RelationshipTo)


# Classes representing relationships between individual nodes that can hold additional information
class BaseProvRel(StructuredRel):
    identifier = StringProperty()
    attributes = JSONProperty()


class WasGeneratedBy(BaseProvRel):
    time = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%S')


class Used(BaseProvRel):
    time = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%S')


class WasInvalidatedBy(BaseProvRel):
    time = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%S')


class WasDerivedFrom(BaseProvRel):
    activity = StringProperty()
    generation = StringProperty()
    usage = StringProperty()


class WasInformedBy(BaseProvRel):
    pass


class WasStartedBy(BaseProvRel):
    starter = StringProperty()
    time = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%S')


class WasEndedBy(BaseProvRel):
    ender = StringProperty()
    time = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%S')


class WasAttributedTo(BaseProvRel):
    pass


class WasAssociatedWith(BaseProvRel):
    plan = StringProperty()


class ActedOnBehalfOf(BaseProvRel):
    activity = StringProperty()


class WasInfluencedBy(BaseProvRel):
    pass


# Fake nodes which are used when opposite node is not present in graph
class BaseFakeProvClass(StructuredNode):
    # avoids giving a tag 'BaseFakeProvClass' in neo4j
    __abstract_node__ = True

    bundled_in = RelationshipTo('Bundle', 'bundled_in')


class FakeActivity(BaseFakeProvClass):
    pass


class FakeAgent(BaseFakeProvClass):
    pass


class FakeEntity(BaseFakeProvClass):
    pass


### Classes for main PROV-DM types ###
class BaseProvClass(StructuredNode):
    # avoids giving a tag 'BaseProvClass' in neo4j
    __abstract_node__ = True

    identifier = StringProperty(required=True)
    attributes = JSONProperty()

    bundled_in = RelationshipTo('Bundle', 'bundled_in')
    was_influenced_by = RelationshipTo('BaseProvClass', 'was_influenced_by', model=WasInfluencedBy)


class Entity(BaseProvClass):
    was_generated_by = RelationshipTo('Activity', 'was_generated_by', model=WasGeneratedBy)
    was_generated_by_fake = RelationshipTo('FakeActivity', 'was_generated_by', model=WasGeneratedBy)

    was_derived_from = RelationshipTo('Entity', 'was_derived_from', model=WasDerivedFrom)

    was_invalidated_by = RelationshipTo('Activity', 'was_invalidated_by', model=WasInvalidatedBy)
    was_invalidated_by_fake = RelationshipTo('FakeActivity', 'was_invalidated_by', model=WasInvalidatedBy)

    was_attributed_to = RelationshipTo('Agent', 'was_attributed_to', model=WasAttributedTo)
    specialization_of = RelationshipTo('Entity', 'specialization_of')
    alternate_of = RelationshipTo('Entity', 'alternate_of')
    had_member = RelationshipTo('Entity', 'had_member')


class Activity(BaseProvClass):
    start_time = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%S')
    end_time = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%S')

    used = RelationshipTo('Entity', 'used', model=Used)
    used_fake = RelationshipTo('FakeEntity', 'used', model=Used)

    was_informed_by = RelationshipTo('Activity', 'was_informed_by', model=WasInformedBy)

    was_associated_with = RelationshipTo('Agent', 'was_associated_with', model=WasAssociatedWith)
    was_associated_with_fake = RelationshipTo('FakeAgent', 'was_associated_with', model=WasAssociatedWith)

    was_started_by = RelationshipTo('Entity', 'was_started_by', model=WasStartedBy)
    was_started_by_fake = RelationshipTo('FakeEntity', 'was_started_by', model=WasStartedBy)

    was_ended_by = RelationshipTo('Entity', 'was_ended_by', model=WasEndedBy)
    was_ended_by_fake = RelationshipTo('FakeEntity', 'was_ended_by', model=WasEndedBy)


class Agent(BaseProvClass):
    acted_on_behalf_of = RelationshipTo('Agent', 'acted_on_behalf_of', model=ActedOnBehalfOf)


class Bundle(BaseProvClass):
    graph = StringProperty()
    signature = StringProperty()
    timestamp = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%S')


class Document(StructuredNode):
    identifier = StringProperty()
    graph = StringProperty()
