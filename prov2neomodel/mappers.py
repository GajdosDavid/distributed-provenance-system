from abc import ABC, abstractmethod
from prov.model import *
from provenance.models import *


class BaseElementMapper(ABC):

    def __init__(self, prov_elem):
        self._prov_elem = prov_elem
        self._neo_elem = None

        self._initialize_model()

    def get_neomodel(self):
        return self._neo_elem

    @abstractmethod
    def do_mapping(self):
        pass

    @abstractmethod
    def _initialize_model(self):
        pass

    def _add_attributes(self):
        if self._prov_elem.attributes:
            attr_dict = {str(key): str(value) for key, value in self._prov_elem.attributes}
            self._neo_elem.attributes = attr_dict


class ProvEntityMapper(BaseElementMapper):

    def _initialize_model(self):
        self._neo_elem = Entity()

    def do_mapping(self):
        self._neo_elem.identifier = self._prov_elem.identifier
        self._add_attributes()


class ProvAgentMapper(BaseElementMapper):

    def _initialize_model(self):
        self._neo_elem = Agent()

    def do_mapping(self):
        self._neo_elem.identifier = self._prov_elem.identifier
        self._add_attributes()


class ProvActivityMapper(BaseElementMapper):

    def _initialize_model(self):
        self._neo_elem = Activity()

    def do_mapping(self):
        self._neo_elem.identifier = self._prov_elem.identifier
        self._neo_elem.start_time = self._prov_elem.get_startTime()
        self._neo_elem.end_time = self._prov_elem.get_endTime()
        self._add_attributes()


prov2neo_mappers = {
    ProvEntity: ProvEntityMapper,
    ProvAgent: ProvAgentMapper,
    ProvActivity: ProvActivityMapper
}