# DailyRunStartExection

Helper for starting a `DailyETLPipeline` execution for the current Dash organisation.

This helper calls the `/dailyRun/start_execution` endpoint on the main Dash v2 API (for example `https://cg.api.comodash.io/v2/dailyRun/start_execution`) and returns the JSON payload as a Python dictionary.

> **Note**  
> This document describes the high-level usage pattern, building on top of the low-level client in this package.  
> For the full Dash SDK helper implementation, see `comotion.dash.DailyRun.start_execution`.

## HTTP details

- **Base URL**: `https://api.{orgname}.comodash.io/superset`
- **Method**: `POST`
- **Path**: `/dailyRun/start_execution`
- **Headers**:
  - `Authorization: Bearer <access-token>`
  - `Accept: application/json`
  - `Content-Type: application/json`
- **Body**:
  - empty JSON body (the endpoint only needs authentication and organisation context)

## Example

The snippet below is adapted from `DailyRuntests.ipynb` and shows how to start a DailyRun execution:

```python
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

# Start a DailyRun execution
response = daily_run.start_execution()
print(response)
```

### Direct HTTP example (without helper)

```python
import os
import requests

orgname = "qainitech"
access_token = os.environ["BEARER_TOKEN"]

base_url = f"https://api.{orgname}.comodash.io/superset"
url = f"{base_url}/dailyRun/start_execution"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

response = requests.post(url, headers=headers)
response.raise_for_status()

payload = response.json()
print(payload)
```

### Parameters

`verify` – `bool | str`, default `True`  
This is passed directly to `requests.post` as the `verify` argument:

- `True` – enable TLS certificate verification using system defaults (recommended for production)
- `False` – disable TLS certificate verification (not recommended for production)
- `"/path/to/ca-bundle.pem"` – use a specific CA bundle for verification

### Return type

`Dict[str, Any]` – the JSON payload returned by the `/dailyRun/start_execution` endpoint.

### Errors

`DailyRun.start_execution` will raise a `ValueError` if:

- the underlying HTTP request to `/dailyRun/start_execution` fails, or
- the response is not `2xx`, or
- the response cannot be parsed as JSON.

If you consistently receive `404`, `401`, or other unexpected errors from this endpoint, please contact Comotion support to ensure the `/dailyRun` endpoints (including `/dailyRun/start_execution`) have been implemented and enabled for your organisation.

