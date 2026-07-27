DailyRun helper
===============

The :class:`DailyRun <comotion.dash.DailyRun>` helper class in :mod:`comotion.dash`
provides a convenient way to work with the ``/dailyRun`` endpoints of the Dash API.
It lets you:

* check whether the daily run is enabled for your organisation
* enable or disable the daily run
* inspect Daily ETL pipeline execution history and status
* start a new Daily ETL pipeline execution

The helper handles access tokens and base URLs for you, and checks that your
credentials are entitled to use the endpoints before making a request.

.. note::

   The ``/dailyRun`` endpoints are not enabled for all organisations by default.
   If the examples below return repeated ``404``, ``401`` or other unexpected errors,
   please contact Comotion support to ensure the ``/dailyRun`` endpoints have been
   implemented and enabled for your organisation.


Endpoint summary
################

All four endpoints are served from the per-organisation frontend API at
``https://api.{orgname}.comodash.io/superset``:

.. list-table::
   :header-rows: 1

   * - Method and path
     - SDK method
     - Required scope
   * - ``GET /dailyRun/dailyRun_enabled``
     - :meth:`DailyRun.get_daily_run_enabled <comotion.dash.DailyRun.get_daily_run_enabled>`
     - ``dailyrun:enabled:read``
   * - ``POST /dailyRun/dailyRun_enabled``
     - :meth:`DailyRun.update_daily_run_enabled <comotion.dash.DailyRun.update_daily_run_enabled>`
     - ``dailyrun:enabled:write``
   * - ``GET /dailyRun/execution_status``
     - :meth:`DailyRun.get_execution_info <comotion.dash.DailyRun.get_execution_info>`
     - ``dailyrun:execution:read``
   * - ``POST /dailyRun/start_execution``
     - :meth:`DailyRun.start_execution <comotion.dash.DailyRun.start_execution>`
     - ``dailyrun:execution:write``


Required permissions
####################

The ``/dailyRun`` endpoints sit behind a JWT authorizer on API Gateway. For a
request to be accepted, your access token must:

* be issued for the ``dash_api`` **audience**, and
* carry a **scope** appropriate to the operation.

There are four scopes, split into two independent families:

.. list-table::
   :header-rows: 1

   * - Scope
     - Grants
   * - ``dailyrun:execution:read``
     - Inspect Daily ETL execution history and status.
   * - ``dailyrun:execution:write``
     - Trigger pipeline runs.
   * - ``dailyrun:enabled:read``
     - Read whether the daily run is enabled.
   * - ``dailyrun:enabled:write``
     - Enable or disable the daily run.

All four scopes are independent. Each endpoint requires exactly one of them, so
``write`` does **not** imply ``read``: to both read and change the daily run
setting you need ``dailyrun:enabled:read`` *and* ``dailyrun:enabled:write``.

Superset dashboard access is separate and still requires ``superset:user`` on
the appropriate client.

Scopes are granted in Comotion Auth against your user or your application client,
so there is nothing to configure in the SDK itself. The helper decodes your token
and checks the scope and audience before sending a request, so a missing
entitlement raises an
:class:`UnAuthenticatedException <comotion.auth.UnAuthenticatedException>`
naming what is missing, rather than an opaque ``403``.

If you see that error, ask your Comotion administrator to grant the appropriate
``dailyrun:*`` scope on the ``dash_api`` audience to the user or application you
are authenticating as.

You can inspect what your own token carries:

.. code-block:: python

   import jwt

   from comotion.auth import Auth

   auth = Auth(orgname="org")
   claims = jwt.decode(auth.get_access_token(), options={"verify_signature": False})

   print("scopes:   ", claims.get("scope"))
   print("audiences:", claims.get("aud"))


Prerequisites
#############

All of the examples below assume that:

* you have the :mod:`comotion-sdk <comotion.dash>` installed and configured
* your organisation has a Dash Daily ETL pipeline set up
* your credentials have the permissions described above

Both authentication styles work. As an application, using a client id and secret:

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

Or as a user, after running ``comotion authenticate`` on the command line:

.. code-block:: python

   from comotion.dash import DashConfig, DailyRun
   from comotion.auth import Auth

   auth = Auth(orgname="org")

   config = DashConfig(auth=auth)
   daily_run = DailyRun(config)


Checking whether the daily run is enabled
#########################################

:meth:`DailyRun.get_daily_run_enabled <comotion.dash.DailyRun.get_daily_run_enabled>`
returns a simple boolean.

.. code-block:: python

   enabled = daily_run.get_daily_run_enabled()
   print(f"Daily run is currently enabled: {enabled}")

If your organisation has no daily run setting recorded against it, the API
responds with a ``404`` and the helper raises a ``ValueError``. Contact Comotion
support to have the setting created.

HTTP details
************

* **Base URL**: ``https://api.{orgname}.comodash.io/superset``
* **Method**: ``GET``
* **Path**: ``/dailyRun/dailyRun_enabled``
* **Headers**:

  * ``Authorization: Bearer <access-token>``
  * ``Accept: application/json``
  * ``Content-Type: application/json``

* **Response**: ``{"dailyRun": <bool>}``

Direct HTTP example (without helper)
************************************

.. code-block:: python

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


Enabling or disabling the daily run
###################################

:meth:`DailyRun.update_daily_run_enabled <comotion.dash.DailyRun.update_daily_run_enabled>`
sets the value and returns what the API stored.

.. code-block:: python

   # Read the current value
   print(f"Initial value: {daily_run.get_daily_run_enabled()}")

   # Turn the daily run on
   print(f"After enabling: {daily_run.update_daily_run_enabled(True)}")

   # Turn the daily run off again
   print(f"After disabling: {daily_run.update_daily_run_enabled(False)}")

HTTP details
************

* **Base URL**: ``https://api.{orgname}.comodash.io/superset``
* **Method**: ``POST``
* **Path**: ``/dailyRun/dailyRun_enabled``
* **Headers**:

  * ``Authorization: Bearer <access-token>``
  * ``Accept: application/json``
  * ``Content-Type: application/json``

* **Body**: ``{"dailyRun": <bool>}``
* **Response**: ``{"dailyRun": <bool>}``

Direct HTTP example (without helper)
************************************

.. code-block:: python

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


Inspecting DailyRun execution status
####################################

:meth:`DailyRun.get_execution_info <comotion.dash.DailyRun.get_execution_info>`
retrieves execution status information for the Daily ETL pipeline and returns the
JSON payload as a Python dictionary.

Use the ``DailyRun.GetDailyRunExecutionMode`` enum to control what is returned:

* ``LIST`` – a list of recent executions (the default)
* ``LATEST`` – the most recent execution, or ``None`` if there are none
* ``LAST_SUCCESSFUL`` – the most recent succeeded execution

The optional ``limit`` argument caps how many executions are considered. The API
clamps it to between 1 and 200, and defaults to 50.

Example
*******

.. code-block:: python

   from pprint import pprint

   modes = DailyRun.GetDailyRunExecutionMode

   # List of recent executions
   pprint(daily_run.get_execution_info(mode=modes.LIST))

   # Latest execution (regardless of status)
   pprint(daily_run.get_execution_info(mode=modes.LATEST))

   # Last successful execution
   pprint(daily_run.get_execution_info(mode=modes.LAST_SUCCESSFUL))

   # Only look at the ten most recent executions
   pprint(daily_run.get_execution_info(mode=modes.LIST, limit=10))

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

In ``LATEST`` and ``LAST_SUCCESSFUL`` modes a single execution object is returned
rather than a list.

HTTP details
************

* **Base URL**: ``https://api.{orgname}.comodash.io/superset``
* **Method**: ``GET``
* **Path**: ``/dailyRun/execution_status``
* **Headers**:

  * ``Authorization: Bearer <access-token>``
  * ``Accept: application/json``
  * ``Content-Type: application/json``

* **Query string parameters**:

  * ``mode`` – one of ``list``, ``latest`` or ``last_successful``. Defaults to ``list``.
  * ``limit`` – optional integer, clamped to between 1 and 200. Defaults to 50.

.. note::

   ``mode`` and ``limit`` are read from the **query string**. Sending them in a
   request body has no effect and the endpoint will silently fall back to
   ``list`` mode.


Starting a DailyRun execution
#############################

:meth:`DailyRun.start_execution <comotion.dash.DailyRun.start_execution>` starts a
Daily ETL pipeline execution for the current organisation.

The pipeline only starts if the daily run is enabled for the organisation. When it
is disabled the API still responds with a ``200``, and the returned payload has
``started`` set to False.

Example
*******

.. code-block:: python

   response = daily_run.start_execution()

   if response["started"]:
       print(f"Started {response['executionName']}")
   else:
       print(response["message"])

Typical response structure
**************************

.. code-block:: python

   {
       "message": "Daily ETL pipeline execution started.",
       "started": True,
       "executionArn": "arn:aws:states:eu-west-1:...:execution:DailyETLPipeline:...",
       "startDate": "2026-01-08T10:02:14.025000+00:00",
       "executionName": "DailyScheduledETL_org_20260108T100213Z",
       "stateMachineArn": "arn:aws:states:eu-west-1:...:stateMachine:DailyETLPipeline",
   }

TLS verification
****************

The ``verify`` argument is passed directly through to :mod:`requests`:

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

* **Body**: none – the endpoint only needs authentication and organisation context
