from neomodel import (StructuredRel, StructuredNode, UniqueIdProperty,
                      StringProperty, JSONProperty, DateTimeFormatProperty, RelationshipTo, RelationshipFrom,
                      cardinality)

'''
class BundledIn(StructuredRel):
    identifier = StringProperty()
    attributes = JSONProperty()
'''


### Classes representing prov-dm relations between PROV-DM types (require both nodes) ###
class BaseProvRel(StructuredRel):
    identifier = StringProperty()
    attributes = JSONProperty()


class WasGeneratedByRel(BaseProvRel):
    time = DateTimeFormatProperty()


class UsedRel(BaseProvRel):
    time = DateTimeFormatProperty()


class WasInvalidatedByRel(BaseProvRel):
    time = DateTimeFormatProperty()


class WasDerivedFromRel(BaseProvRel):
    activity = StringProperty()
    generation = StringProperty()
    usage = StringProperty()


class WasInformedBy(BaseProvRel):
    pass


class WasAttributedTo(BaseProvRel):
    pass


class WasAssociatedWithRel(BaseProvRel):
    plan = StringProperty()


class ActedOnBehalfOfRel(BaseProvRel):
    activity = StringProperty()


class WasInfluencedBy(BaseProvRel):
    pass


### Classes representing PROV-DM relations, however are modeled as neo4j nodes because they allow absence of one of the PROV-DM types ###
class BaseProvRelNode(StructuredNode):
    identifier = StringProperty()
    attributes = JSONProperty()

    bundled_in = RelationshipTo('Bundle', 'bundled_in')


class WasGeneratedBy(BaseProvRelNode):
    entity = RelationshipFrom('Entity', 'was_generated_by', cardinality.One)

    activity = RelationshipTo('Activity', 'was_generated_by', cardinality.ZeroOrOne)

    time = DateTimeFormatProperty()


class Used(BaseProvRelNode):
    activity = RelationshipFrom('Activity', 'used', cardinality.One)

    entity = RelationshipTo('Entity', 'used', cardinality.ZeroOrOne)

    time = DateTimeFormatProperty()


class WasStartedBy(BaseProvRelNode):
    activity = RelationshipFrom('Activity', 'was_started_by', cardinality.One)

    trigger = RelationshipTo('Entity', 'was_started_by', cardinality.ZeroOrOne)
    starter = RelationshipTo('Activity', 'was_started_by', cardinality.ZeroOrOne)

    time = DateTimeFormatProperty()


class WasEndedBy(BaseProvRelNode):
    activity = RelationshipFrom('Activity', 'was_ended_by', cardinality.One)

    trigger = RelationshipTo('Entity', 'was_ended_by', cardinality.ZeroOrOne)
    ender = RelationshipTo('Activity', 'was_ended_by', cardinality.ZeroOrOne)

    time = DateTimeFormatProperty()


class WasInvalidatedBy(BaseProvRelNode):
    entity = RelationshipFrom('Entity', 'was_invalidated_by', cardinality.One)

    activity = RelationshipTo('Activity', 'was_invalidated_by', cardinality.ZeroOrOne)

    time = DateTimeFormatProperty()


class WasAssociatedWith(BaseProvRelNode):
    activity = RelationshipFrom('Activity', 'was_associated_with', cardinality.One)

    agent = RelationshipTo('Agent', 'was_associated_with', cardinality.ZeroOrOne)
    plan = RelationshipTo('Entity', 'was_associated_with', cardinality.ZeroOrOne)


class ActedOnBehalfOf(BaseProvRelNode):
    delegate = RelationshipFrom('Agent', 'acted_on_behalf_of', cardinality.One)
    responsible = RelationshipTo('Agent', 'acted_on_behalf_of', cardinality.One)

    activity = RelationshipTo('Activity', 'acted_on_behalf_of', cardinality.ZeroOrOne)

### Classes for main PROV-DM types ###
class BaseProvClass(StructuredNode):
    identifier = StringProperty(required=True)
    attributes = JSONProperty()

    bundled_in = RelationshipTo('Bundle', 'bundled_in')

    # TODO -- might not be correct and might be necessary to move this somewhere else as the relationship can be between all PROV-DM types
    was_influenced_by = RelationshipTo('BaseProvClass', 'was_influenced_by', model=WasInfluencedBy)


class Entity(BaseProvClass):
    was_derived_from = RelationshipTo('Entity', 'was_derived_from', model=WasDerivedFromRel)
    was_generated_by = RelationshipTo('Activity', 'was_generated_by', model=WasGeneratedByRel)
    was_invalidated_by = RelationshipTo('Activity', 'was_invalidated_by', model=WasInvalidatedByRel)
    was_attributed_to = RelationshipTo('Agent', 'was_attributed_to', model=WasAttributedTo)
    specialization_of = RelationshipTo('Entity', 'specialization_of')
    alternate_of = RelationshipTo('Entity', 'alternate_of')


class Activity(BaseProvClass):
    start_time = DateTimeFormatProperty()
    end_time = DateTimeFormatProperty()

    was_informed_by = RelationshipTo('Activity', 'was_informed_by', model=WasInformedBy)
    used = RelationshipTo('Entity', 'used', model=UsedRel)
    was_associated_with = RelationshipTo('Agen', 'was_associated_with', model=WasAssociatedWithRel)

    # was_started_by?
    # was_ended_by?


class Agent(BaseProvClass):
    acted_on_behalf_of = RelationshipTo('Agen', 'acted_on_behalf_of', model=ActedOnBehalfOfRel)
    

class Bundle(BaseProvClass):
    pass

# TODO -- missing collections and hadMember() relation