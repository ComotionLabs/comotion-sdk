# DailyRunStartExection

Helper for starting a `DailyETLPipeline` execution for the current Dash organisation.

This helper calls the `/dailyRun/start_execution` endpoint on the per-organisation frontend API (for example `https://api.org.comodash.io/superset/dailyRun/start_execution`) and returns the JSON payload as a Python dictionary.

Starting a run manually is **not** gated by the daily-run enabled flag — that flag only controls the scheduled nightly kickoff. A manual run starts unless a pipeline run is already in progress for the organisation. When one is already running the API responds with `409` and a payload where `started` is `False` (see below); the helper returns that payload rather than raising, so inspect `started` to distinguish the two outcomes.

> **Note**  
> This document describes the high-level usage pattern, building on top of the low-level client in this package.  
> For the full Dash SDK helper implementation, see `comotion.dash.DailyRun.start_execution`.

## Required permissions

The `/dailyRun` endpoints are protected by a JWT authorizer. Your access token must be issued for the `dash_api` **audience** and carry the **`dailyrun:execution:write` scope**.

Triggering a pipeline run is an operational action, so `dailyrun:execution:read` is **not** sufficient. Conversely, this scope alone does not let you check the resulting execution status — that needs `dailyrun:execution:read` as well.

The helper checks the scope and audience before sending the request and raises `comotion.auth.UnAuthenticatedException` with an explanation if either is missing. Ask your Comotion administrator to grant these to your user or application if you hit that error.

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

On a successful start (`200`), for a client on the legacy pipeline:

```python
{
    "message": "Daily ETL pipeline execution started.",
    "started": True,
    "executionArn": "arn:aws:states:eu-west-1:...:execution:DailyETLPipeline:...",
    "startDate": "2026-01-08T10:02:14.025000+00:00",
    "executionName": "DailyScheduledETL_org_20260108T100213Z",
    "stateMachineArn": "arn:aws:states:eu-west-1:...:stateMachine:DailyETLPipeline",
}
```

The API routes per organisation: clients with `insights_v2` set to boolean `true` in `ClientMetaData` run `DailyETLPipelineV2` and their `executionName` is prefixed `DailyScheduledETLV2_`; everyone else runs `DailyETLPipeline` with the `DailyScheduledETL_` prefix.

When a run is already in progress (`409`), the helper returns the payload instead of raising:

```python
{
    "message": "Daily ETL pipeline is already running for this client; no execution started.",
    "started": False,
    "executionName": None,
    "runningExecution": {
        "name": "DailyScheduledETL_org_20260108T100213Z",
        "status": "RUNNING",
        "startDate": "2026-01-08T10:02:14.025000+00:00",
    },
    "stateMachineArn": "arn:aws:states:eu-west-1:...:stateMachine:DailyETLPipeline",
}
```

### Errors

`DailyRun.start_execution` raises `UnAuthenticatedException` if the token is missing the required scope or audience, or if the API responds with `401` or `403`.

It raises a `ValueError` if:

- the underlying HTTP request to `/dailyRun/start_execution` fails, or
- the response is not `2xx` and not the `409` already-running case described above, or
- the response cannot be parsed as JSON.

If you consistently receive `404`, `401`, or other unexpected errors from this endpoint, please contact Comotion support to ensure the `/dailyRun` endpoints (including `/dailyRun/start_execution`) have been implemented and enabled for your organisation.

