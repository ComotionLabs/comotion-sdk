# DailyRunStartExecution

Helper for starting a `DailyETLPipeline` execution for the current Dash organisation.

This helper calls the `/dailyRun/start_execution` endpoint on the per-organisation frontend API (for example `https://api.org.comodash.io/superset/dailyRun/start_execution`) and returns a `StartExecutionResponse` model.

Starting a run manually is **not** gated by the daily-run enabled flag — that flag only controls the scheduled nightly kickoff. A manual run starts unless a pipeline run is already in progress for the organisation. When one is already running the API responds with `409` and a payload where `started` is `False` (see below); the helper returns that payload rather than raising, so inspect `started` to distinguish the two outcomes.

> **Note**  
> This document describes the high-level usage pattern, building on top of the generated `comodash_dailyrun_api_client_lowlevel` package.  
> For the full Dash SDK helper implementation, see `comotion.dash.DailyRun.start_execution`.

## Required permissions

The `/dailyRun` endpoints are protected by a JWT authorizer. Your access token must be issued for the `dash_api` **audience** and carry the **`dailyrun:execution:write` scope**.

Triggering a pipeline run is an operational action, so `dailyrun:execution:read` is **not** sufficient. Conversely, this scope alone does not let you check the resulting execution status — that needs `dailyrun:execution:read` as well.

The helper checks the scope and audience before sending the request and raises `comotion.auth.UnAuthenticatedException` with an explanation if either is missing. Ask your Comotion administrator to grant these to your user or application if you hit that error.

## HTTP details

- **Base URL**: `https://api.{orgname}.comodash.io/superset` (or `comodash.com` via `DashConfig(..., dns_suffix="comodash.com")`)
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

### TLS

TLS verification follows ``DashConfig``, the same as ``Query`` and ``Load``. Set
``config.verify_ssl`` or ``config.ssl_ca_cert`` before creating ``DailyRun(config)``.

### Return type

`StartExecutionResponse` – the same generated model for both outcomes, so `started` is what distinguishes them.

On a successful start (`200`):

```python
response.started            # True
response.message            # Daily ETL pipeline execution started.
response.execution_arn      # arn:aws:states:eu-west-1:...:execution:DailyETLPipeline:...
response.start_date         # 2026-01-08T10:02:14.025000+00:00
response.execution_name     # DailyScheduledETL_org_20260108T100213Z
response.state_machine_arn  # arn:aws:states:eu-west-1:...:stateMachine:DailyETLPipeline
```

Manual runs always target `DailyETLPipeline`. The scheduled nightly kickoff
may still route `insights_v2` clients to `DailyETLPipelineV2` separately.

When a run is already in progress (`409`), the helper returns the model instead of raising:

```python
response.started                    # False
response.execution_name             # None
response.message                    # Daily ETL pipeline is already running for this client; no execution started.
response.running_execution.name     # DailyScheduledETL_org_20260108T100213Z
response.running_execution.status   # RUNNING
response.running_execution.start_date  # 2026-01-08T10:02:14.025000+00:00
response.state_machine_arn          # arn:aws:states:eu-west-1:...:stateMachine:DailyETLPipeline
```

Model fields are snake_case where the JSON uses camelCase. Call `.to_dict()` on the response for the original shape.

### Errors

`DailyRun.start_execution` raises `UnAuthenticatedException` if the token is missing the required scope or audience, or if the API responds with `401` or `403`.

It raises a `ValueError` if:

- the underlying HTTP request to `/dailyRun/start_execution` fails, or
- the response is not `2xx` and not the `409` already-running case described above, or
- the response cannot be parsed as JSON.

If you consistently receive `404`, `401`, or other unexpected errors from this endpoint, please contact Comotion support to ensure the `/dailyRun` endpoints (including `/dailyRun/start_execution`) have been implemented and enabled for your organisation.

