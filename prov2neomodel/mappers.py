from abc import ABC, abstractmethod
from prov.model import *
from provenance.models import *


def convert_tuple_list_to_dict(tuple_list: list) -> dict:
    out = {}

    for key, value in tuple_list:
        key = str(key)
        value = str(value)

        if key in out:
            if isinstance(out[key], list):
                out[key].append(value)
            else:
                out[key] = [value, out[key]]
        else:
            out[key] = value

    return out


class BaseElementMapper(ABC):

    def __init__(self, bundle, prov_elem):
        self._prov_elem = prov_elem
        self._bundle = bundle
        self._neo_elem = None

        self._initialize_model()

    def get_neomodel(self):
        return self._neo_elem

    def map(self):
        self._neo_elem.identifier = self._prov_elem.identifier
        self._add_attributes()

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def _initialize_model(self):
        pass

    def _add_attributes(self):
        if self._prov_elem.attributes:
            attr_dict = convert_tuple_list_to_dict(self._prov_elem.attributes)
            self._neo_elem.attributes = attr_dict


class ProvEntityMapper(BaseElementMapper):

    def _initialize_model(self):
        self._neo_elem = Entity()

    def save(self):
        self.map()

        self._neo_elem.save()
        self._neo_elem.bundled_in.connect(self._bundle)


class ProvAgentMapper(BaseElementMapper):

    def _initialize_model(self):
        self._neo_elem = Agent()

    def save(self):
        self.map()

        self._neo_elem.save()
        self._neo_elem.bundled_in.connect(self._bundle)


class ProvActivityMapper(BaseElementMapper):

    def _initialize_model(self):
        self._neo_elem = Activity()

    def map(self):
        super().map()
        self._neo_elem.start_time = self._prov_elem.get_startTime()
        self._neo_elem.end_time = self._prov_elem.get_endTime()

    def save(self):
        self.map()

        self._neo_elem.save()
        self._neo_elem.bundled_in.connect(self._bundle)


class BaseRelMapper(ABC):

    def __init__(self, bundle, prov_rel, neo_nodes: dict):
        self._bundle = bundle
        self._prov_rel = prov_rel
        self._neo_nodes = neo_nodes

    @abstractmethod
    def save(self):
        pass

    def _populate_common_fields(self, to_populate):
        to_populate.identifier = self._prov_rel.identifier

        if self._prov_rel.extra_attributes:
            attr_dict = convert_tuple_list_to_dict(self._prov_rel.extra_attributes)
            to_populate.attributes = attr_dict


class ProvGenerationMapper(BaseRelMapper):
    ENTITY = 0
    ACTIVITY = 1
    TIME = 2

    def save(self):
        activity = self._prov_rel.args[self.ACTIVITY]
        entity = self._prov_rel.args[self.ENTITY]

        rel = WasGeneratedBy()
        self._populate_fields(rel)

        neo_entity = self._neo_nodes[entity]
        if activity:
            neo_activity = self._neo_nodes[activity]

            neo_entity.was_generated_by.connect(neo_activity, rel.__dict__)
        else:
            fake_activity = FakeActivity()
            fake_activity.save()
            fake_activity.bundled_in.connect(self._bundle)

            neo_entity.was_generated_by_fake.connect(fake_activity, rel.__dict__)

    def _populate_fields(self, to_populate):
        self._populate_common_fields(to_populate)

        to_populate.time = self._prov_rel.args[self.TIME]


class ProvUsageMapper(BaseRelMapper):
    ACTIVITY = 0
    ENTITY = 1
    TIME = 2

    def save(self):
        activity = self._prov_rel.args[self.ACTIVITY]
        entity = self._prov_rel.args[self.ENTITY]

        rel = Used()
        self._populate_fields(rel)

        neo_activity = self._neo_nodes[activity]
        if entity:
            neo_entity = self._neo_nodes[entity]
            neo_activity.used.connect(neo_entity, rel.__dict__)
        else:
            fake_entity = FakeEntity()
            fake_entity.save()
            fake_entity.bundled_in.connect(self._bundle)

            neo_activity.used_fake.connect(fake_entity, rel.__dict__)

    def _populate_fields(self, to_populate):
        self._populate_common_fields(to_populate)

        to_populate.time = self._prov_rel.args[self.TIME]


class ProvCommunicationMapper(BaseRelMapper):
    INFORMED = 0
    INFORMANT = 1

    def save(self):
        informed = self._prov_rel.args[self.INFORMED]
        informant = self._prov_rel.args[self.INFORMANT]

        rel = WasInformedBy()
        self._populate_common_fields(rel)

        neo_informed = self._neo_nodes[informed]
        neo_informant = self._neo_nodes[informant]
        neo_informant.was_informed_by.connect(neo_informed, rel.__dict__)


class ProvStartMapper(BaseRelMapper):
    ACTIVITY = 0
    TRIGGER = 1
    STARTER = 2
    TIME = 3

    def save(self):
        activity = self._prov_rel.args[self.ACTIVITY]
        trigger = self._prov_rel.args[self.TRIGGER]

        rel = WasStartedBy()
        self._populate_fields(rel)

        neo_activity = self._neo_nodes[activity]
        if trigger:
            neo_entity = self._neo_nodes[trigger]
            neo_activity.was_started_by.connect(neo_entity, rel.__dict__)
        else:
            fake_entity = FakeEntity()
            fake_entity.save()
            fake_entity.bundled_in.connect(self._bundle)

            neo_activity.was_started_by_fake.connect(fake_entity, rel.__dict__)

    def _populate_fields(self, to_populate):
        self._populate_common_fields(to_populate)

        to_populate.time = self._prov_rel.args[self.TIME]
        to_populate.starter = self._prov_rel.args[self.STARTER]  # TODO Test!!


class ProvEndMapper(BaseRelMapper):
    ACTIVITY = 0
    TRIGGER = 1
    ENDER = 2
    TIME = 3

    def save(self):
        activity = self._prov_rel.args[self.ACTIVITY]
        trigger = self._prov_rel.args[self.TRIGGER]

        rel = WasEndedBy()
        self._populate_fields(rel)

        neo_activity = self._neo_nodes[activity]
        if trigger:
            neo_entity = self._neo_nodes[trigger]
            neo_activity.was_ended_by.connect(neo_entity, rel.__dict__)
        else:
            fake_entity = FakeEntity()
            fake_entity.save()
            fake_entity.bundled_in.connect(self._bundle)

            neo_activity.was_ended_by_fake.connect(fake_entity, rel.__dict__)

    def _populate_fields(self, to_populate):
        self._populate_common_fields(to_populate)

        to_populate.time = self._prov_rel.args[self.TIME]
        to_populate.ender = self._prov_rel.args[self.ENDER]  # TODO Test!!


class ProvInvalidationMapper(BaseRelMapper):
    ENTITY = 0
    ACTIVITY = 1
    TIME = 2

    def save(self):
        entity = self._prov_rel.args[self.ENTITY]
        activity = self._prov_rel.args[self.ACTIVITY]

        rel = WasInvalidatedBy()
        self._populate_fields(rel)

        neo_entity = self._neo_nodes[entity]
        if activity:
            neo_activity = self._neo_nodes[activity]
            neo_entity.was_invalidated_by.connect(neo_activity, rel.__dict__)
        else:
            fake_activity = FakeActivity()
            fake_activity.save()
            fake_activity.bundled_in.connect(self._bundle)

            neo_entity.was_invalidated_by_fake.connect(fake_activity, rel.__dict__)

    def _populate_fields(self, to_populate):
        self._populate_common_fields(to_populate)

        to_populate.time = self._prov_rel.args[self.TIME]


class ProvDerivationMapper(BaseRelMapper):
    GENERATED_ENTITY = 0
    USED_ENTITY = 1
    ACTIVITY = 2
    GENERATION = 3
    USAGE = 4

    def save(self):
        generated_entity = self._prov_rel.args[self.GENERATED_ENTITY]
        used_entity = self._prov_rel.args[self.USED_ENTITY]

        rel = WasDerivedFrom()
        self._populate_fields(rel)

        neo_generated_entity = self._neo_nodes[generated_entity]
        neo_used_entity = self._neo_nodes[used_entity]
        neo_generated_entity.was_derived_from.connect(neo_used_entity, rel.__dict__)

    def _populate_fields(self, to_populate):
        self._populate_common_fields(to_populate)

        to_populate.activity = self._prov_rel.args[self.ACTIVITY]
        to_populate.generation = self._prov_rel.args[self.GENERATION]
        to_populate.usage = self._prov_rel.args[self.USAGE]


class ProvAttributionMapper(BaseRelMapper):
    ENTITY = 0
    AGENT = 1

    def save(self):
        entity = self._prov_rel.args[self.ENTITY]
        agent = self._prov_rel.args[self.AGENT]

        rel = WasAttributedTo()
        self._populate_common_fields(rel)

        neo_entity = self._neo_nodes[entity]
        neo_agent = self._neo_nodes[agent]
        neo_entity.was_attributed_to.connect(neo_agent, rel.__dict__)


class ProvAssociationMapper(BaseRelMapper):
    ACTIVITY = 0
    AGENT = 1
    PLAN = 2

    def save(self):
        activity = self._prov_rel.args[self.ACTIVITY]
        agent = self._prov_rel.args[self.AGENT]

        rel = WasAssociatedWith()
        self._populate_fields(rel)

        neo_activity = self._neo_nodes[activity]
        if agent:
            neo_agent = self._neo_nodes[agent]
            neo_activity.was_associated_with.connect(neo_agent, rel.__dict__)
        else:
            fake_agent = FakeAgent()
            fake_agent.save()
            fake_agent.bundled_in.connect(self._bundle)

            neo_activity.was_associated_with_fake.connect(fake_agent, rel.__dict__)

    def _populate_fields(self, to_populate):
        self._populate_common_fields(to_populate)

        to_populate.plan = self._prov_rel.args[self.PLAN]


class ProvDelegationMapper(BaseRelMapper):
    DELEGATE = 0
    RESPONSIBLE = 1
    ACTIVITY = 2

    def save(self):
        delegate = self._prov_rel.args[self.DELEGATE]
        responsible = self._prov_rel.args[self.RESPONSIBLE]

        rel = ActedOnBehalfOf()
        self._populate_fields(rel)

        neo_delegate = self._neo_nodes[delegate]
        neo_responsible = self._neo_nodes[responsible]
        neo_delegate.acted_on_behalf_of.connect(neo_responsible, rel.__dict__)

    def _populate_fields(self, to_populate):
        self._populate_common_fields(to_populate)

        to_populate.activity = self._prov_rel.args[self.ACTIVITY]


class ProvInfluenceMapper(BaseRelMapper):
    INFLUENCEE = 0
    INFLUENCER = 1

    def save(self):
        influencee = self._prov_rel.args[self.INFLUENCEE]
        influencer = self._prov_rel.args[self.INFLUENCER]

        rel = WasInfluencedBy()
        self._populate_common_fields(rel)

        neo_influencee = self._neo_nodes[influencee]
        neo_influencer = self._neo_nodes[influencer]
        neo_influencee.was_influenced_by.connect(neo_influencer, rel.__dict__)


class ProvSpecializationMapper(BaseRelMapper):
    INFRA = 0
    SUPRA = 1

    def save(self):
        infra = self._prov_rel.args[self.INFRA]
        supra = self._prov_rel.args[self.SUPRA]

        neo_infra = self._neo_nodes[infra]
        neo_supra = self._neo_nodes[supra]
        neo_infra.specialization_of.connect(neo_supra)


class ProvAlternateMapper(BaseRelMapper):
    ALT1 = 0
    ALT2 = 1

    def save(self):
        alt1 = self._prov_rel.args[self.ALT1]
        alt2 = self._prov_rel.args[self.ALT2]

        neo_alt1 = self._neo_nodes[alt1]
        neo_alt2 = self._neo_nodes[alt2]
        neo_alt1.alternate_of.connect(neo_alt2)


class ProvMentionMapper(BaseRelMapper):
    # TODO

    def save(self):
        pass


class ProvMembershipMapper(BaseRelMapper):
    COLLECTION = 0
    ENTITY = 1

    def save(self):
        collection = self._prov_rel.args[self.COLLECTION]
        entity = self._prov_rel.args[self.ENTITY]

        neo_collection = self._neo_nodes[collection]
        neo_entity = self._neo_nodes[entity]
        neo_collection.had_member.connect(neo_entity)


prov2neo_mappers = {
    ProvEntity: ProvEntityMapper,
    ProvAgent: ProvAgentMapper,
    ProvActivity: ProvActivityMapper,

    ProvGeneration: ProvGenerationMapper,
    ProvUsage: ProvUsageMapper,
    ProvCommunication: ProvCommunicationMapper,
    ProvStart: ProvStartMapper,
    ProvEnd: ProvEndMapper,
    ProvInvalidation: ProvInvalidationMapper,
    ProvDerivation: ProvDerivationMapper,
    ProvAttribution: ProvAttributionMapper,
    ProvAssociation: ProvAssociationMapper,
    ProvDelegation: ProvDelegationMapper,
    ProvInfluence: ProvInfluenceMapper,
    ProvSpecialization: ProvSpecializationMapper,
    ProvAlternate: ProvAlternateMapper,
    ProvMention: ProvMentionMapper,
    ProvMembership: ProvMembershipMapper
}
