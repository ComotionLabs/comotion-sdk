DailyRun helper
===============

The :class:`DailyRun <comotion.dash.DailyRun>` helper class in :mod:`comotion.dash`
provides a convenient way to work with the ``/dailyRun`` endpoints of the Dash API.
It lets you:

* check whether the DailyRun feature flag is enabled for your organisation
* update the DailyRun flag
* inspect DailyRun execution history and status
* start a new DailyRun execution

These helpers sit on top of the low-level Dash v2 API client in
``comodash_api_client_lowlevel`` and handle access tokens and base URLs for you.

.. note::

   The ``/dailyRun`` endpoints are not enabled for all organisations by default.
   If the examples below return repeated ``404``, ``401`` or other unexpected errors,
   please contact Comotion support to ensure the ``/dailyRun`` endpoints have been
   implemented and enabled for your organisation.


Prerequisites
#############

All of the examples below assume that:

* you have the :mod:`comotion-sdk <comotion.dash>` installed and configured
* your organisation has a Dash Daily ETL pipeline set up
* you have an application client id and secret that can act on behalf of your organisation

The authentication pattern is the same in all cases:

.. code-block:: python

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


Checking the DailyRun flag status
#################################

The :meth:`DailyRun.get_flag_status <comotion.dash.DailyRun.get_flag_status>` method
checks whether the DailyRun feature flag is enabled for the current Dash organisation.
Internally it calls the ``/dailyRun/flag_status`` endpoint and returns a simple boolean.

.. code-block:: python

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

   flag_status = daily_run.get_flag_status()
   print(f"DailyRun flag is currently set to: {flag_status}")

HTTP details
************

* **Base URL**: ``https://api.{orgname}.comodash.io/superset``
* **Method**: ``GET``
* **Path**: ``/dailyRun/flag_status``
* **Headers**:

  * ``Authorization: Bearer <access-token>``
  * ``Accept: application/json``
  * ``Content-Type: application/json``

Direct HTTP example (without helper)
************************************

If you already have a valid access token (for example obtained via
:meth:`Auth.get_access_token <comotion.auth.Auth.get_access_token>` or from an
environment variable), you can call the endpoint directly:

.. code-block:: python

   import os
   import requests

   orgname = "org"
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


Updating the DailyRun flag status
#################################

The :meth:`DailyRun.update_flag_status <comotion.dash.DailyRun.update_flag_status>`
method updates the DailyRun feature flag for the current organisation and returns
the resulting value as a boolean.

.. code-block:: python

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

   # Read the current flag value
   current_status = daily_run.get_flag_status()
   print(f"Initial DailyRun flag: {current_status}")

   # Turn the flag on
   enabled = daily_run.update_flag_status(True)
   print(f"DailyRun flag after enabling: {enabled}")

   # Turn the flag off again
   disabled = daily_run.update_flag_status(False)
   print(f"DailyRun flag after disabling: {disabled}")

HTTP details
************

* **Base URL**: ``https://api.{orgname}.comodash.io/superset``
* **Method**: ``POST``
* **Path**: ``/dailyRun/flag_status``
* **Headers**:

  * ``Authorization: Bearer <access-token>``
  * ``Accept: application/json``
  * ``Content-Type: application/json``

* **Body**:

  * JSON object: ``{"dailyRun": <bool>}``

Direct HTTP example (without helper)
************************************

.. code-block:: python

   import os
   import requests

   orgname = "org"
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


Inspecting DailyRun execution status
####################################

The :meth:`DailyRun.get_execution_info <comotion.dash.DailyRun.get_execution_info>`
method retrieves execution status information for the Daily ETL pipeline.
It calls ``/dailyRun/execution_status`` and returns the JSON payload as a
Python dictionary.

You can control how much information is returned using the
``DailyRun.GetDailyRunExecutionMode`` enum:

* ``DailyRun.GetDailyRunExecutionMode.LIST`` – list of recent executions
* ``DailyRun.GetDailyRunExecutionMode.LATEST`` – the latest execution
* ``DailyRun.GetDailyRunExecutionMode.LAST_SUCCESSFUL`` – the last successful execution

Example
*******

.. code-block:: python

   from pprint import pprint

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

Typical response structure for ``LIST`` mode
********************************************

.. code-block:: python

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

HTTP details
************

* **Base URL**: ``https://api.{orgname}.comodash.io/superset``
* **Method**: ``GET``
* **Path**: ``/dailyRun/execution_status``
* **Headers**:

  * ``Authorization: Bearer <access-token>``
  * ``Accept: application/json``
  * ``Content-Type: application/json``

* **Body**:

  * JSON object: ``{"mode": "<list|latest|last_successful>"}``


Starting a DailyRun execution
#############################

The :meth:`DailyRun.start_execution <comotion.dash.DailyRun.start_execution>` method
starts a Daily ETL pipeline execution for the current organisation. It calls
``/dailyRun/start_execution`` and returns the JSON payload as a dictionary.

Example
*******

.. code-block:: python

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

   # Start a DailyRun execution
   response = daily_run.start_execution()
   print(response)

TLS verification
****************

The ``verify`` argument is passed directly to :func:`requests.post`:

* ``True`` – enable TLS certificate verification using system defaults (recommended)
* ``False`` – disable TLS certificate verification (not recommended for production)
* ``"/path/to/ca-bundle.pem"`` – use a specific CA bundle for verification

HTTP details
************

* **Base URL**: ``https://api.{orgname}.comodash.io/superset``
* **Method**: ``POST``
* **Path**: ``/dailyRun/start_execution``
* **Headers**:

  * ``Authorization: Bearer <access-token>``
  * ``Accept: application/json``
  * ``Content-Type: application/json``

* **Body**:

  * empty JSON body – the endpoint only needs authentication and organisation context

