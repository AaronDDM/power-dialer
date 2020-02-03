# PowerDialer

This is a `PowerDialer` service which will concurrently dial (`PowerDialer.DIAL_RATIO` number of) leads for a given agent. The `PowerDial` is expected to be called based on
_events_ that occur outside of the PowerDialer service.

## Usage

See unit tests for more examples.

```python
from power_dialer import PowerDialer, Database

# e.g. A an logs into a mobile app
powerDialer = PowerDialer(agent_id=1)
powerDialer.on_agent_login()
# ...
powerDialer.on_agent_logout()

# e.g. A Dialer service has successfully started a call 
powerDialer.on_call_started(lead_phone_number='19051235285')
# ...
powerDialer.on_call_failed(lead_phone_number='19051235285')
# ...
powerDialer.on_call_ended(lead_phone_number='19051235285')
```

## Run Tests
```bash
python3 -m unittest discover tests
```

## Assumptions
- An external service (e.g. an App or an external Dialer service) will be responsible for invoking the methods of this PowerDialer
  - e.g. When an Agent logs into n App, the `PowerDialer.on_agent_login()` is invoked.
  - e.g. When the Dialer service is used, it will be responsible for sending an event to the PowerDialer later on to invoke the `PowerDialer.on_call_started()` or PowerDialer.on_call_failed() event.
- When `Dialer.get_lead_phone_number()` is called, the lead phone number is taken out from the "queue" and is no longer useable by other agents (this is simulated).
- The database can be any database - we currently mocked a database and even provided it with simulated delays. This mock database is also used for unit testing - in a production app, we would only use the mock for testing purposes.
