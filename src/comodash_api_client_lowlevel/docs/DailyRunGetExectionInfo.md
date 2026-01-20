# DailyRunGetExectionInfo

Helper for retrieving execution status information for the `DailyETLPipeline` associated with the current Dash organisation.

This helper calls the `/dailyRun/execution_status` endpoint on the Dash API and returns the JSON payload as a Python dictionary.

> **Note**  
> This document describes the high-level usage pattern, building on top of the low-level client in this package.  
> For the full Dash SDK helper implementation, see `comotion.dash.DailyRun.get_execution_info`.

## HTTP details

- **Base URL**: `https://api.{orgname}.comodash.io/superset`
- **Method**: `GET`
- **Path**: `/dailyRun/execution_status`
- **Headers**:
  - `Authorization: Bearer <access-token>`
  - `Accept: application/json`
  - `Content-Type: application/json`
- **Body**:
  - JSON object: `{"mode": "<list|latest|last_successful>"}` (sent by the helper)

## Execution modes

The helper exposes an `Enum` on the `DailyRun` class to control how much information is returned:

- `DailyRun.GetDailyRunExecutionMode.LIST` – list of recent executions
- `DailyRun.GetDailyRunExecutionMode.LATEST` – the latest execution
- `DailyRun.GetDailyRunExecutionMode.LAST_SUCCESSFUL` – the last successful execution

## Example

The snippet below is adapted from `DailyRuntests.ipynb` and shows how to:

- authenticate and configure Dash
- choose an execution mode
- inspect the returned execution payload

```python
from pprint import pprint

from comotion.dash import DashConfig, DailyRun
from comotion.auth import Auth

org_name = "org"
entity_type = Auth.APPLICATION
application_client_id = "application_id"
application_client_secret = "application_secret"

auth = Auth(
    orgname=org_name,
    entity_type=entity_type,
    application_client_id=application_client_id,
    application_client_secret=application_client_secret,
)

config = DashConfig(auth=auth)
daily_run = DailyRun(config)

modes = DailyRun.GetDailyRunExecutionMode

# List of recent executions
execution_status_list = daily_run.get_execution_info(mode=modes.LIST)
pprint(execution_status_list)

# Latest execution (regardless of status)
execution_status_latest = daily_run.get_execution_info(mode=modes.LATEST)
pprint(execution_status_latest)

# Last successful execution
execution_status_last_successful = daily_run.get_execution_info(mode=modes.LAST_SUCCESSFUL)
pprint(execution_status_last_successful)
```

### Direct HTTP example (without helper)

```python
import os
import requests
from pprint import pprint

orgname = "qainitech"
access_token = os.environ["BEARER_TOKEN"]

base_url = f"https://api.{orgname}.comodash.io/superset"
url = f"{base_url}/dailyRun/execution_status"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

response = requests.get(url, headers=headers, json={"mode": "list"})
response.raise_for_status()

payload = response.json()
pprint(payload)
```

### Return type

`Dict[str, Any]` – the JSON payload returned by the `/dailyRun/execution_status` endpoint.

For `LIST` mode this is typically a structure like:

```python
{
    "executions": [
        {
            "name": "DailyScheduledETL_org_20260108T100213Z",
            "status": "FAILED",
            "startDate": "2026-01-08T10:02:14.025000+00:00",
            "stopDate": "2026-01-08T10:02:16.253000+00:00",
        },
        # ...
    ]
}
```

### Errors

`DailyRun.get_execution_info` will raise a `ValueError` if:

- `mode` is not an instance of `DailyRun.GetDailyRunExecutionMode`, or
- the underlying HTTP request to `/dailyRun/execution_status` fails, or
- the response cannot be parsed as JSON.

If you consistently receive `404`, `401`, or other unexpected errors from this endpoint, please contact Comotion support to ensure the `/dailyRun` endpoints (including `/dailyRun/execution_status`) have been implemented and enabled for your organisation.

