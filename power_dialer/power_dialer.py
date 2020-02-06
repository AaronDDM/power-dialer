import concurrent.futures
from .error.dialer_error import DialerError
from .error.power_dialer_error import PowerDialerError
from .service.db import Database
from .service.dialer import Dialer, DialerStatus

class PowerDialer:
    DIAL_RATIO: int = 2

    def __init__(self, agent_id: str, db: Database, dialer: Dialer):
        self.db = db
        self.dialer = dialer
        self.agent_id = agent_id
        self.futures: dict = {}

    def on_agent_login(self):
        return self.dial()

    def on_agent_logout(self):
        delete_leads_to_be_called = self.db.delete_all_leads_to_be_called(agent_id=self.agent_id)
        if delete_leads_to_be_called is False:
            raise PowerDialerError('[on_agent_logout] Unable to delete all leads to be called for the agent %s' % (self.agent_id))

        delete_agent_on_call = self.db.delete_agent_on_call(
            agent_id=self.agent_id)
        if delete_agent_on_call is False:
            raise PowerDialerError(
                '[on_agent_logout] Unable to delete all records for the agent being on call for the agent %s' % (self.agent_id))
        
        return True

    def on_call_started(self, lead_phone_number: str):
        if self.db.delete_lead_to_be_called(agent_id=self.agent_id, lead_phone_number=lead_phone_number): 
            on_call = self.db.check_if_agent_on_call(agent_id=self.agent_id)
            if on_call is False:
                self.db.insert_agent_on_call(
                    agent_id=self.agent_id, lead_phone_number=lead_phone_number)
                return True
        else:
            raise PowerDialerError('[on_call_started] Unable to delete lead %s from leads to be called list for agent %s' % (lead_phone_number, self.agent_id))

    def on_call_failed(self, lead_phone_number: str):
        if self.db.delete_lead_to_be_called(agent_id=self.agent_id, lead_phone_number=lead_phone_number):
            return self.dial()
        else:
            raise PowerDialerError('[on_call_failed] Unable to delete lead %s from leads to be called list for agent %s' % (lead_phone_number, self.agent_id))

    def on_call_ended(self, lead_phone_number: str):
        delete_agent_on_call = self.db.delete_agent_on_call(
            agent_id=self.agent_id)
        if delete_agent_on_call is True:
            return self.dial()
        else:
            raise PowerDialerError('[on_call_ended] Unable to mark the agent\'s call as having ended for the agent %s' % (self.agent_id))

    # This method is responsible for initaiting the 
    # concurrent dialing self.DIAL_RATIO leads 
    # at a time for a given self.agent_id.
    #
    # Note: If an agent is already dialing a lead 
    # and this method is called again - it will only dial
    # (DIAL_RATIO - # of leads currently being called) for the
    # given agent. This maintains the DIAL_RATIO # of calls.
    def dial(self):
        total_new_leads_to_dial = PowerDialer.DIAL_RATIO - \
            self.db.fetch_total_leads_being_called(agent_id=self.agent_id)

        inserted_leads = True
        for i in range(total_new_leads_to_dial):
            if inserted_leads is True:
                try:
                    lead_phone_number = self.dialer.get_lead_phone_number_to_dial()
                except DialerError as err:
                    raise PowerDialerError(
                        '[dial] An error occurred while attempting to fetch a lead phone number: %s' % (err))
                else:
                    inserted_leads = self.db.insert_lead_to_be_called(
                        agent_id=self.agent_id, lead_phone_number=lead_phone_number)
        
        if inserted_leads is False:
            raise PowerDialerError('[dial] An error occurred while attempting to insert a lead into the to be called database for agent %s' % (self.agent_id))
            
        return self.multi_threaded_dial()

    # When called, we spin up DIAL_RATIO threads
    # and call the Dialer servicer for all
    # leads to be called in the database for the given self.agent_id
    def multi_threaded_dial(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.DIAL_RATIO) as executor:
            leads = self.db.fetch_leads_being_called(agent_id=self.agent_id)

            self.futures = {
                executor.submit(self.dialer.dial, self.agent_id, lead_phone_number): lead_phone_number for lead_phone_number in leads
            }

            for future in concurrent.futures.as_completed(self.futures):
                lead = self.futures[future]
                try:
                    data = future.result()
                    return True
                except Exception as exc:
                    return self.on_call_failed(lead_phone_number=lead['lead_phone_number'])
