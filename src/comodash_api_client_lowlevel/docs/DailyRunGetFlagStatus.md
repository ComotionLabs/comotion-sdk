# DailyRunGetFlagStatus

Helper for checking whether the `DailyRun` feature flag is enabled for the current Dash organisation.

This helper ultimately calls the `/dailyRun/flag_status` endpoint on the Dash API and returns the result as a simple boolean.

> **Note**  
> This document describes the high-level usage pattern, building on top of the low-level client in this package.  
> For the full Dash SDK helper implementation, see `comotion.dash.DailyRun.get_flag_status`.

## HTTP details

- **Base URL**: `https://api.{orgname}.comodash.io/superset`
- **Method**: `GET`
- **Path**: `/dailyRun/flag_status`
- **Headers**:
  - `Authorization: Bearer <access-token>`
  - `Accept: application/json`
  - `Content-Type: application/json`

## Example

The snippet below is adapted from the `DailyRuntests.ipynb` notebook and shows how to:

- authenticate using `comotion.auth.Auth`
- create a `DashConfig`
- construct a `DailyRun` helper
- read the current `DailyRun` flag value

```python
import jwt
from comotion.dash import DashConfig, DailyRun
from comotion.auth import Auth

org_name = "org"
entity_type = Auth.APPLICATION
application_client_id = "application_id"
application_client_secret = "application_secret"

# Authenticate for the organisation
auth = Auth(
    orgname=org_name,
    entity_type=entity_type,
    application_client_id=application_client_id,
    application_client_secret=application_client_secret,
)

# Build Dash configuration (zone is optional; defaults are used if omitted)
config = DashConfig(auth=auth)

# (Optional) Inspect the decoded access token
access_token = auth.get_access_token()
access_token_decoded = jwt.decode(access_token, options={"verify_signature": False})
print(access_token_decoded)

# Check the DailyRun flag status
daily_run = DailyRun(config)
flag_status = daily_run.get_flag_status()
print(f"DailyRun flag is currently set to: {flag_status}")
```

### Direct HTTP example (without helper)

If you already have a valid access token (for example obtained via `Auth.get_access_token()` or from environment), you can call the endpoint directly with `requests`:

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

response = requests.get(url, headers=headers)
response.raise_for_status()

payload = response.json()
flag_status = payload["DailyRun"]
print(flag_status)
```

### Return type

`bool` – `True` if the `DailyRun` flag is enabled for the organisation, `False` otherwise.

### Errors

`DailyRun.get_flag_status` will raise a `ValueError` if:

- the underlying HTTP request to `/dailyRun/flag_status` fails, or
- the response cannot be parsed as JSON, or
- the JSON payload does not contain a boolean `DailyRun` field.

If you consistently receive `404`, `401`, or other unexpected errors from this endpoint, please contact Comotion support to ensure the `/dailyRun` endpoints (including `/dailyRun/flag_status`) have been implemented and enabled for your organisation.

