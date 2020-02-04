import random
import time
from enum import Enum
from .db import Database
from ..error.dialer_error import DialerError
from ..error.database_error import DatabaseError
from random import randint

class DialerStatus(Enum): 
    STARTED = 0
    FAILED = 1
    DIALING = 2

class Dialer:
    def __init__(self, db: Database, disable_simulation: bool = False):
        self.db = db
        self.disable_simulation = disable_simulation

    def get_lead_phone_number_to_dial(self):
        try:
            lead = self.db.fetch_lead()
        except DatabaseError as err:
            raise DialerError('No lead phone number to return')
        else:
            return lead['phone_number']

    def dial(self, agent_id: str, lead_phone_number: str):
        self._simulateDelay()
        self.db.insert_lead_called(agent_id=agent_id, lead_phone_number=lead_phone_number)
        return DialerStatus.DIALING

    def _simulateDelay(self):
        if self.disable_simulation is False:
            randomSeconds = random.randrange(0, 2)
            if randomSeconds > 0:
                time.sleep(randomSeconds)
