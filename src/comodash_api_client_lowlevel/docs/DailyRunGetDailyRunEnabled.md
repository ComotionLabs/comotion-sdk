# DailyRunGetDailyRunEnabled

Helper for checking whether the daily run is enabled for the current Dash organisation.

This helper calls the `/dailyRun/dailyRun_enabled` endpoint on the Dash API and returns the result as a simple boolean.

> **Note**  
> This document describes the high-level usage pattern, building on top of the low-level client in this package.  
> For the full Dash SDK helper implementation, see `comotion.dash.DailyRun.get_daily_run_enabled`.

## Required permissions

The `/dailyRun` endpoints are protected by a JWT authorizer. Your access token must be issued for the `dash_api` **audience** and carry the **`dailyrun:enabled:read` scope**.

`dailyrun:enabled:write` does not grant access here — it only permits changing the setting.

The helper checks the scope and audience before sending the request and raises `comotion.auth.UnAuthenticatedException` with an explanation if either is missing. Ask your Comotion administrator to grant these to your user or application if you hit that error.

## HTTP details

- **Base URL**: `https://api.{orgname}.comodash.io/superset`
- **Method**: `GET`
- **Path**: `/dailyRun/dailyRun_enabled`
- **Headers**:
  - `Authorization: Bearer <access-token>`
  - `Accept: application/json`
  - `Content-Type: application/json`
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

enabled = daily_run.get_daily_run_enabled()
print(f"Daily run is currently enabled: {enabled}")
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

response = requests.get(url, headers=headers)
response.raise_for_status()

print(response.json()["dailyRun"])
```

### Return type

`bool` – `True` if the daily run is enabled for the organisation, `False` otherwise.

### Errors

`DailyRun.get_daily_run_enabled` raises `UnAuthenticatedException` if the token is missing the required scope or audience, or if the API responds with `401` or `403`.

It raises a `ValueError` if:

- the underlying HTTP request fails, or
- the API responds with any other non-2xx status, or
- the response cannot be parsed as JSON, or
- the JSON payload does not contain a boolean `dailyRun` field.

A `404` means the organisation has no daily run setting recorded against it. Contact Comotion support to have the setting created.
