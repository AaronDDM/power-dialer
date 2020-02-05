import unittest
import concurrent.futures
import threading
from unittest.mock import Mock
from power_dialer import PowerDialer
from power_dialer.service.db import Database
from power_dialer.service.dialer import Dialer
from power_dialer.error.dialer_error import DialerError
from power_dialer.error.power_dialer_error import PowerDialerError

class TestPowerDialer(unittest.TestCase):
    def setUp(self):
        # Because this DB is essentially a mock DB - we can use it for testing as well!
        self.db = Database(disable_simulation=True)
        self.dialer = Dialer(db=self.db, disable_simulation=True)
        self.power_dialer = PowerDialer(agent_id=1, db=self.db, dialer=self.dialer)

    def test_power_dialer_init(self):
        self.assertTrue(isinstance(self.power_dialer, PowerDialer),
                        msg='Successfully initiated our PowerDialer class.')

    def test_power_dialer_on_agent_login(self):
        self.power_dialer.on_agent_login()
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)

        self.assertEqual(self.db.calling_leads.__len__(), PowerDialer.DIAL_RATIO, msg='Expect to have %d lead(s) being called.' % PowerDialer.DIAL_RATIO)
                        
    def test_power_dialer_on_call_started(self):
        self.power_dialer.on_agent_login()
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)

        self.assertEqual(self.db.calling_leads.__len__(), PowerDialer.DIAL_RATIO, msg='Expect to have %d lead(s) being called.' % PowerDialer.DIAL_RATIO)

        self.power_dialer.on_call_started('19274718724')

        expected_leads_called = (PowerDialer.DIAL_RATIO - 1)
        self.assertEqual(self.db.calling_leads.__len__(), expected_leads_called, msg='Expect to have %d lead(s) being called.' % expected_leads_called)
        self.assertEqual(self.db.agents_on_call.__len__(), 1, msg='Expect to have 1 agents being on call.')

    def test_power_dialer_on_call_started_exception(self):
        mock = Mock()
        db = Database()
        db.delete_lead_to_be_called = mock
        mock.return_value = False


        dialer = Dialer(db=db, disable_simulation=True)
        power_dialer = PowerDialer(agent_id=1, db=db, dialer=dialer)

        power_dialer.on_agent_login()
        finished, pending = concurrent.futures.wait(power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)
        
        self.assertRaises(PowerDialerError, power_dialer.on_call_started, 1)

    def test_power_dialer_on_call_failed(self):
        self.power_dialer.on_agent_login()
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)
            
        self.power_dialer.on_call_failed('19274718724')
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)

        # If a lead call failed, we should have dialed
        # a new lead - so our leads being called should be PowerDialer.DIAL_RATIO
        self.assertEqual(self.db.calling_leads.__len__(), PowerDialer.DIAL_RATIO, msg='Expect to have %d lead(s) being called.' % PowerDialer.DIAL_RATIO)

    def test_power_dialer_on_call_ended(self):
        self.power_dialer.on_agent_login()
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)

        self.power_dialer.on_call_ended('19274718724')
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)

        # After a call has ended - we start re-dialing leads
        # that means we should have PowerDialer.DIAL_RATIO leads being calledOh 
        self.assertEqual(self.db.calling_leads.__len__(), PowerDialer.DIAL_RATIO, msg='Expect to have %d lead(s) being called.' % PowerDialer.DIAL_RATIO)

    def test_power_dialer_on_agent_logout(self):
        self.power_dialer.on_agent_login()
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)

        self.assertEqual(self.db.calling_leads.__len__(), PowerDialer.DIAL_RATIO, msg='Expect to have %d lead(s) being called.' % PowerDialer.DIAL_RATIO)

        self.power_dialer.on_call_started('19274718724')
        self.assertEqual(self.db.agents_on_call.__len__(), 1, msg='Expect to have 1 agents being on call.')

        self.power_dialer.on_call_ended('19274718724')
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)
        
        self.power_dialer.on_agent_logout()

        self.assertEqual(self.db.calling_leads.__len__(), 0, msg='Expect to have 0 leads being called.')
        self.assertEqual(self.db.agents_on_call.__len__(), 0, msg='Expect to have 0 agents being on call.')

    def test_power_dialer_failed_dials(self):
        dialer = Dialer(db=self.db, disable_simulation=False)

        mock = Mock()
        dialer.get_lead_phone_number_to_dial = mock
        mock.return_value = self.mock_get_lead_phone_number

        power_dialer = PowerDialer(agent_id=1, db=self.db, dialer=dialer)

        self.power_dialer.on_agent_login()
        finished, pending = concurrent.futures.wait(self.power_dialer.futures, 0, concurrent.futures.ALL_COMPLETED)

        self.assertEqual(self.db.leads.__len__(), 2, msg='Expect to have only 2 leads remaining.')

    def test_power_dialer_dial_exception(self):
        dialer = Dialer(db=self.db, disable_simulation=False)

        mock = Mock(side_effect=DialerError('No lead phone number to return'))
        dialer.get_lead_phone_number_to_dial = mock

        power_dialer = PowerDialer(agent_id=1, db=self.db, dialer=dialer)

        self.assertRaises(PowerDialerError, power_dialer.dial)

    def mock_get_lead_phone_number():
        try:
            lead = self.db.fetch_lead()
        except DatabaseError as err:
            raise DialerError('No lead phone number to return')
        else:
            if (lead['phone_number'] == '19274718724' or lead['phone_number'] == '14719284724'):
                raise DialerError(
                    'An error occurred while dialing %s' % lead['phone_number'])
            else:
                return lead['phone_number']
