# DailyRunUpdateFlagStatus

Helper for updating the `DailyRun` feature flag for the current Dash organisation.

This helper ultimately calls the `/dailyRun/flag_status` endpoint on the Dash API with a `POST` request and returns the resulting flag value as a boolean.

> **Note**  
> This document describes the high-level usage pattern, building on top of the low-level client in this package.  
> For the full Dash SDK helper implementation, see `comotion.dash.DailyRun.update_flag_status`.

## HTTP details

- **Base URL**: `https://api.{orgname}.comodash.io/superset`
- **Method**: `POST`
- **Path**: `/dailyRun/flag_status`
- **Headers**:
  - `Authorization: Bearer <access-token>`
  - `Accept: application/json`
  - `Content-Type: application/json`
- **Body**:
  - JSON object: `{"dailyRun": <bool>}`

## Example

The snippet below is adapted from `DailyRuntests.ipynb` and shows how to:

- authenticate using `comotion.auth.Auth`
- create a `DashConfig`
- construct a `DailyRun` helper
- toggle the `DailyRun` flag on and off

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

# Read the current flag value
current_status = daily_run.get_flag_status()
print(f"Initial DailyRun flag: {current_status}")

# Turn the flag on
updated_status = daily_run.update_flag_status(True)
print(f"DailyRun flag after enabling: {updated_status}")

# Turn the flag off again
updated_status = daily_run.update_flag_status(False)
print(f"DailyRun flag after disabling: {updated_status}")
```

### Direct HTTP example (without helper)

```python
import os
import requests

orgname = "qainitech"
access_token = os.environ["BEARER_TOKEN"]

base_url = f"https://api.{orgname}.comodash.io/superset"
url = f"{base_url}/dailyRun/flag_status"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

body = {
    "dailyRun": True,  # or False
}

response = requests.post(url, headers=headers, json=body)
response.raise_for_status()

payload = response.json()
print(payload.get("DailyRun", payload.get("dailyRun")))
```

### Parameters

`new_status` – `bool`  
The new boolean value to set for the `DailyRun` flag.

### Return type

`bool` – the updated value of the `DailyRun` flag as returned by the API.

### Errors

`DailyRun.update_flag_status` will raise:

- `TypeError` if `new_status` is not a boolean
- `ValueError` if:
  - the underlying HTTP request to `/dailyRun/flag_status` fails, or
  - the response cannot be parsed as JSON, or
  - the JSON payload does not contain a boolean `DailyRun` / `dailyRun` field.

If you consistently receive `404`, `401`, or other unexpected errors from this endpoint, please contact Comotion support to ensure the `/dailyRun` endpoints (including `/dailyRun/flag_status`) have been implemented and enabled for your organisation.

