# DailyRunUpdateDailyRunEnabled

Helper for enabling or disabling the daily run for the current Dash organisation.

This helper calls the `/dailyRun/dailyRun_enabled` endpoint with a `POST` request and returns the value stored by the API as a boolean.

> **Note**  
> This document describes the high-level usage pattern, building on top of the generated `comodash_dailyrun_api_client_lowlevel` package.  
> For the full Dash SDK helper implementation, see `comotion.dash.DailyRun.update_daily_run_enabled`.

## Required permissions

The `/dailyRun` endpoints are protected by a JWT authorizer. Your access token must be issued for the `dash_api` **audience** and carry the **`dailyrun:enabled:write` scope**.

Turning the daily ETL on or off is a configuration change, so `dailyrun:enabled:read` is **not** sufficient here. Conversely, this scope alone does not let you read the setting back — that needs `dailyrun:enabled:read` as well.

The helper checks the scope and audience before sending the request and raises `comotion.auth.UnAuthenticatedException` with an explanation if either is missing. Ask your Comotion administrator to grant these to your user or application if you hit that error.

## HTTP details

- **Base URL**: `https://api.{orgname}.comodash.io/superset`
- **Method**: `POST`
- **Path**: `/dailyRun/dailyRun_enabled`
- **Headers**:
  - `Authorization: Bearer <access-token>`
  - `Accept: application/json`
  - `Content-Type: application/json`
- **Body**: `{"dailyRun": <bool>}`
- **Response**: `{"dailyRun": <bool>}`

## Example

```python
from comotion.dash import DashConfig, DailyRun
from comotion.auth import Auth

auth = Auth(
    orgname="org",
    entity_type=Auth.APPLICATION,
    application_client_id="application_id",
    application_client_secret="application_secret",
)

config = DashConfig(auth=auth)
daily_run = DailyRun(config)

# Read the current value
print(f"Initial value: {daily_run.get_daily_run_enabled()}")

# Turn the daily run on
print(f"After enabling: {daily_run.update_daily_run_enabled(True)}")

# Turn the daily run off again
print(f"After disabling: {daily_run.update_daily_run_enabled(False)}")
```

### Direct HTTP example (without helper)

```python
import os
import requests

orgname = "org"
access_token = os.environ["BEARER_TOKEN"]

base_url = f"https://api.{orgname}.comodash.io/superset"
url = f"{base_url}/dailyRun/dailyRun_enabled"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

response = requests.post(url, headers=headers, json={"dailyRun": True})
response.raise_for_status()

print(response.json()["dailyRun"])
```

### Return type

`bool` – the value stored by the API.

### Errors

`DailyRun.update_daily_run_enabled` raises a `TypeError` if `enabled` is not a boolean.

It raises `UnAuthenticatedException` if the token is missing the required scope or audience, or if the API responds with `401` or `403`.

It raises a `ValueError` if:

- the underlying HTTP request fails, or
- the API responds with any other non-2xx status, or
- the response cannot be parsed as JSON, or
- the JSON payload does not contain a boolean `dailyRun` field.
