# PowerDialer

This is a `PowerDialer` service which will concurrently dial (`PowerDialer.DIAL_RATIO` number of) leads for a given agent. The `PowerDialer` is expected to be called based on
_events_ that occur outside of the PowerDialer service.

## Usage

See unit tests for more examples.

```python
from database import Database # Not part of this repo
from dialer import Dialer # Not part of this repo
from power_dialer import PowerDialer

# Setup
db = Database()
dialer = Dialer(db=db)

# e.g. A an logs into a mobile app
powerDialer = PowerDialer(agent_id=1, db=db)
powerDialer.on_agent_login(dialer=dialer)
# ...
powerDialer.on_agent_logout()

# e.g. A Dialer service has successfully started a call 
powerDialer.on_call_started(lead_phone_number='19051235285')
# ...
powerDialer.on_call_failed(lead_phone_number='19051235285', dialer=dialer)
# ...
powerDialer.on_call_ended(lead_phone_number='19051235285', dialer=dialer)
```

## Run Tests
```bash
python3 -m unittest discover test
```

## Database

Basic structure of the expected database. We are assuming a relational database is being used - but this could also be a key/value or a Document based database as well.

### Tables

| Table Name | Columns | Description |
|------------|---------|-------------|
| agents     | id, name | Used identify a particular agent |
| leads      | lead_phone_number | Contains the leads an agent will dial |
| agents_on_call | agent_id, lead_phone_number | Used to track which agents are currently on a call with a leads |
| calling_leads | agent_id, lead_phone_number | Used to track which lead phone number an agent is calling |
| leads_called | agent_id, lead_phone_number | Used to track which lead phone number was called by which agent |


## Assumptions
- An external service (e.g. an App or an external Dialer service) will be responsible for invoking the (event) methods of this PowerDialer.
  - e.g. When an Agent logs into n App, the `PowerDialer.on_agent_login()` is invoked and the PowerDialer instance is then destroyed.
  - e.g. When the Dialer service is used, it will be responsible for sending an event to the PowerDialer later on to invoke the `PowerDialer.on_call_started()` or PowerDialer.on_call_failed() event, and the PowerDialer instance is then destroyed.
- When `Dialer.get_lead_phone_number()` is called, the lead phone number is taken out from the "queue" and is no longer useable by other agents (this is simulated). It is assumed that in reality, this `Dialer` will call an external service.
  - If a dial fails due to some non-call related error (e.g. network error), the lead is still considered abandoned.
- The database can be any database - however, a relational database (using a library like pymysql) was in mind while designing the currently mocked database. This *mock database is also used for unit testing* - in a production app, we would only use the mock for testing purposes.
