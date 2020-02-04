#!/usr/bin/python3
import random
import time
from ..error.database_error import DatabaseError

class Database: 
    def __init__(self, disable_simulation: bool = False):
        self.agents = {
            1: {
                'id': "123",
                'name': 'Sam'
            }
        }
        self.leads = [
            {'phone_number': "11231231234", "called": False, "agent_id": None},
            {'phone_number': "12325828324", "called": False, "agent_id": None},
            {'phone_number': "14719284724", "called": False, "agent_id": None},
            {'phone_number': "19274718724", "called": False, "agent_id": None}
        ]
        self.leads_called = []
        self.agents_on_call = []
        self.calling_leads = []
        self.disable_simulation = disable_simulation

    def fetch_leads_being_called(self, agent_id: str):
        self._simulateDelay()
        return list(filter(lambda x: x['agent_id'] is agent_id, self.calling_leads))

    def fetch_total_leads_being_called(self, agent_id: str):
        self._simulateDelay()
        return self.fetch_leads_being_called(agent_id=agent_id).__len__()

    def insert_lead_to_be_called(self, agent_id: str, lead_phone_number: str):
        self.calling_leads.append(
            {'agent_id': agent_id, 'lead_phone_number': lead_phone_number})
        self._simulateDelay()
        return True

    def delete_all_leads_to_be_called(self, agent_id: str):
        self._simulateDelay()
        self.calling_leads = list(filter(lambda x: (
            x['agent_id'] != agent_id), self.calling_leads))
        return True

    def delete_lead_to_be_called(self, agent_id: str, lead_phone_number: str):
        self._simulateDelay()

        self.calling_leads = list(filter(lambda x: (
            x['agent_id'] != agent_id or x['lead_phone_number'] != lead_phone_number), self.calling_leads))

        return True

    def check_if_agent_on_call(self, agent_id: str):
        self._simulateDelay()
        return list(filter(lambda x: x['agent_id'] is agent_id, self.agents_on_call)).__len__() > 0

    def fetch_total_agents_on_call(self, agent_id: str):
        self._simulateDelay()
        return self.fetch_leads_being_called(agent_id=agent_id).__len__()

    def insert_agent_on_call(self, agent_id: str, lead_phone_number: str):
        self._simulateDelay()
        self.agents_on_call.append(
            {'agent_id': agent_id, 'lead_phone_number': lead_phone_number})
        return True

    def delete_agent_on_call(self, agent_id: str):
        self._simulateDelay()
        self.agents_on_call = list(filter(lambda x: (
            x['agent_id'] != agent_id), self.agents_on_call))
        return True

    def insert_lead_called(self, agent_id: str, lead_phone_number: str):
        self.leads_called.append(
            {'agent_id': agent_id, 'lead_phone_number': lead_phone_number})
        return True

    def fetch_lead(self):
        self._simulateDelay()
        if self.leads.__len__() > 0:
            return self.leads.pop() 
        else: 
            raise DatabaseError('No new leads found.')

    def update_lead(self, phone_number: str, lead: dict):
        self._simulateDelay()
        agent = self.leads.get(agent_id)
        if agent:
            self.agents.update({**agent, 'online': online, 'on_call': on_call})
        return True
        
    def update_agent(self, agent_id: str):
        self._simulateDelay()
        agent = self.agents.get(agent_id)
        if agent:
            self.agents.update({**agent, 'online': online, 'on_call': on_call})
        return True

    def _simulateDelay(self):
        if self.disable_simulation is False:
            randomSeconds = random.randrange(0, 1)
            if randomSeconds > 0:
                time.sleep(randomSeconds)
