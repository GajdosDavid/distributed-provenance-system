from unittest import TestCase, mock
from . import mappers
from datetime import datetime
from prov.model import ProvEntity, ProvBundle, ProvAgent, ProvActivity


class ElementMappersTestCase(TestCase):
    _bundle = ProvBundle(identifier='Bundle1', namespaces={"ex": "http://example.com/"})

    def test_entity_import(self):
        entity_id = 'entity1'
        attributes = {'prov:type': 'document',
                      'ex:version': '2',
                      'ex:foo': 'bar'}
        prov_entity = ProvEntity(self._bundle, entity_id, attributes)
        mapper = mappers.ProvEntityMapper(None, prov_entity)
        mapper.map_to_neomodel()

        neomodel = mapper.get_neomodel()
        self.assertEqual(neomodel.identifier, entity_id)
        self.assertEqual(neomodel.attributes, attributes)

    def test_agent_import(self):
        agent_id = 'agent1'
        attributes = {'ex:employee': '1234',
                      'ex:name': 'Alice',
                      'prov:type': 'prov:Person'}
        prov_agent = ProvAgent(self._bundle, agent_id, attributes)
        mapper = mappers.ProvAgentMapper(None, prov_agent)
        mapper.map_to_neomodel()

        neomodel = mapper.get_neomodel()
        self.assertEqual(neomodel.identifier, agent_id)
        self.assertEqual(neomodel.attributes, attributes)

    def test_activity_import(self):
        activity_id = 'activity1'
        attributes = {'ex:employee': '1234',
                      'ex:host': "server.example.org",
                      'prov:type': 'ex:edit'}
        prov_activity = ProvActivity(self._bundle, activity_id, attributes)
        start = datetime(2023, 2, 2, 22, 22, 22)
        end = datetime(2024, 1, 2, 3, 4, 5)
        prov_activity.set_time(start, end)
        mapper = mappers.ProvActivityMapper(None, prov_activity)
        mapper.map_to_neomodel()

        neomodel = mapper.get_neomodel()
        self.assertEqual(neomodel.identifier, activity_id)
        self.assertEqual(neomodel.start_time, start)
        self.assertEqual(neomodel.end_time, end)
        self.assertEqual(neomodel.attributes, attributes)
