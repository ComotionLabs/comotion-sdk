import unittest
from unittest.mock import MagicMock, patch

import jwt

from comodash_dailyrun_api_client_lowlevel.exceptions import (
    ApiException,
    ConflictException,
    ForbiddenException,
    ServiceException,
    UnauthorizedException,
)
from comodash_dailyrun_api_client_lowlevel.models.daily_run_enabled import DailyRunEnabled
from comodash_dailyrun_api_client_lowlevel.models.execution import Execution
from comodash_dailyrun_api_client_lowlevel.models.execution_status import ExecutionStatus
from comodash_dailyrun_api_client_lowlevel.models.running_execution import RunningExecution
from comodash_dailyrun_api_client_lowlevel.models.start_execution_response import (
    StartExecutionResponse
)

from comotion.auth import UnAuthenticatedException
from comotion.dash import DailyRun, DashConfig


FULL_ACCESS_CLAIMS = {
    "scope": (
        "openid profile dailyrun:execution:read dailyrun:execution:write "
        "dailyrun:enabled:read dailyrun:enabled:write"
    ),
    "aud": ["dash_api", "account"],
}

EXECUTION_READ_CLAIMS = {
    "scope": "openid profile dailyrun:execution:read",
    "aud": ["dash_api"],
}

EXECUTION_WRITE_CLAIMS = {
    "scope": "openid profile dailyrun:execution:write",
    "aud": ["dash_api"],
}

ENABLED_READ_CLAIMS = {
    "scope": "openid profile dailyrun:enabled:read",
    "aud": ["dash_api"],
}

ENABLED_WRITE_CLAIMS = {
    "scope": "openid profile dailyrun:enabled:write",
    "aud": ["dash_api"],
}


def make_token(claims):
    return jwt.encode(claims, "a" * 32, algorithm="HS256")


def make_config(claims=None):
    config = MagicMock(spec=DashConfig)
    config.daily_run_host_url = "https://api.testorg.comodash.io/superset"
    config.access_token = make_token(FULL_ACCESS_CLAIMS if claims is None else claims)
    return config


class TestDailyRunInit(unittest.TestCase):

    def test_rejects_non_dash_config(self):
        with self.assertRaises(TypeError):
            DailyRun({"not": "a config"})

    def test_accepts_dash_config(self):
        config = make_config()
        self.assertIs(DailyRun(config).config, config)


class TestDailyRunAuthorisation(unittest.TestCase):

    def test_passes_when_scope_and_audience_present(self):
        DailyRun(make_config())._check_authorisation(DailyRun.EXECUTION_READ_SCOPES)

    def test_accepts_audience_as_plain_string(self):
        config = make_config({"scope": "dailyrun:execution:read", "aud": "dash_api"})
        DailyRun(config)._check_authorisation(DailyRun.EXECUTION_READ_SCOPES)

    def test_rejects_missing_scope(self):
        config = make_config({"scope": "openid", "aud": ["dash_api"]})
        with self.assertRaises(UnAuthenticatedException) as context:
            DailyRun(config)._check_authorisation(DailyRun.EXECUTION_READ_SCOPES)
        self.assertIn("dailyrun:execution:read", str(context.exception))

    def test_rejects_missing_audience(self):
        config = make_config({"scope": "dailyrun:execution:write", "aud": ["account"]})
        with self.assertRaises(UnAuthenticatedException) as context:
            DailyRun(config)._check_authorisation(DailyRun.EXECUTION_WRITE_SCOPES)
        self.assertIn("dash_api", str(context.exception))

    def test_superset_user_no_longer_grants_access(self):
        config = make_config({"scope": "superset:user", "aud": ["dash_api"]})
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(config)._check_authorisation(DailyRun.EXECUTION_READ_SCOPES)


@patch("comotion.dash.DailyRunApi")
class TestDailyRunScopeSplit(unittest.TestCase):

    def test_execution_read_can_view_execution_status(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_execution_status.return_value = (
            ExecutionStatus(executions=[])
        )
        DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info()
        mock_api_class.return_value.get_daily_run_execution_status.assert_called_once()

    def test_execution_write_cannot_view_execution_status(self, mock_api_class):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).get_execution_info()
        mock_api_class.return_value.get_daily_run_execution_status.assert_not_called()

    def test_execution_read_cannot_start_execution(self, mock_api_class):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(EXECUTION_READ_CLAIMS)).start_execution()
        mock_api_class.return_value.start_daily_run_execution.assert_not_called()

    def test_execution_write_can_start_execution(self, mock_api_class):
        mock_api_class.return_value.start_daily_run_execution.return_value = (
            StartExecutionResponse(started=True)
        )
        DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()
        mock_api_class.return_value.start_daily_run_execution.assert_called_once()

    def test_execution_scopes_cannot_read_enabled_flag(self, mock_api_class):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_daily_run_enabled()
        mock_api_class.return_value.get_daily_run_enabled.assert_not_called()

    def test_enabled_read_can_read_enabled_flag(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.return_value = (
            DailyRunEnabled(dailyRun=True)
        )
        DailyRun(make_config(ENABLED_READ_CLAIMS)).get_daily_run_enabled()
        mock_api_class.return_value.get_daily_run_enabled.assert_called_once()

    def test_enabled_write_cannot_read_enabled_flag(self, mock_api_class):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(ENABLED_WRITE_CLAIMS)).get_daily_run_enabled()
        mock_api_class.return_value.get_daily_run_enabled.assert_not_called()

    def test_enabled_read_cannot_change_enabled_flag(self, mock_api_class):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(ENABLED_READ_CLAIMS)).update_daily_run_enabled(True)
        mock_api_class.return_value.update_daily_run_enabled.assert_not_called()

    def test_enabled_write_can_change_enabled_flag(self, mock_api_class):
        mock_api_class.return_value.update_daily_run_enabled.return_value = (
            DailyRunEnabled(dailyRun=True)
        )
        DailyRun(make_config(ENABLED_WRITE_CLAIMS)).update_daily_run_enabled(True)
        mock_api_class.return_value.update_daily_run_enabled.assert_called_once()

    def test_enabled_scopes_cannot_view_execution_status(self, mock_api_class):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(ENABLED_READ_CLAIMS)).get_execution_info()
        mock_api_class.return_value.get_daily_run_execution_status.assert_not_called()


@patch("comotion.dash.DailyRunApi")
class TestGetDailyRunEnabled(unittest.TestCase):

    def test_calls_correct_operation_and_returns_flag(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.return_value = (
            DailyRunEnabled(dailyRun=True)
        )
        result = DailyRun(make_config()).get_daily_run_enabled()
        self.assertTrue(result)
        self.assertIsInstance(result, bool)
        mock_api_class.return_value.get_daily_run_enabled.assert_called_once_with()

    def test_returns_false_when_disabled(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.return_value = (
            DailyRunEnabled(dailyRun=False)
        )
        self.assertFalse(DailyRun(make_config()).get_daily_run_enabled())

    def test_targets_the_superset_host(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.return_value = (
            DailyRunEnabled(dailyRun=True)
        )
        daily_run = DailyRun(make_config())
        daily_run.get_daily_run_enabled()
        api_client = mock_api_class.call_args[0][0]
        self.assertEqual(
            api_client.configuration.host,
            "https://api.testorg.comodash.io/superset"
        )


@patch("comotion.dash.DailyRunApi")
class TestGetExecutionInfo(unittest.TestCase):

    def test_mode_is_sent_as_query_parameter(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_execution_status.return_value = (
            ExecutionStatus()
        )
        DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info(
            mode=DailyRun.GetDailyRunExecutionMode.LATEST
        )
        self.assertEqual(
            mock_api_class.return_value.get_daily_run_execution_status.call_args[1],
            {"mode": "latest"}
        )

    def test_defaults_to_list_mode(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_execution_status.return_value = (
            ExecutionStatus(executions=[])
        )
        DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info()
        self.assertEqual(
            mock_api_class.return_value.get_daily_run_execution_status.call_args[1],
            {"mode": "list"}
        )

    def test_limit_is_sent_when_provided(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_execution_status.return_value = (
            ExecutionStatus(executions=[])
        )
        DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info(limit=10)
        self.assertEqual(
            mock_api_class.return_value.get_daily_run_execution_status.call_args[1],
            {"mode": "list", "limit": 10}
        )

    def test_rejects_invalid_mode(self, mock_api_class):
        with self.assertRaises(ValueError):
            DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info(mode="latest")
        mock_api_class.return_value.get_daily_run_execution_status.assert_not_called()

    def test_rejects_boolean_limit(self, mock_api_class):
        with self.assertRaises(ValueError):
            DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info(limit=True)
        mock_api_class.return_value.get_daily_run_execution_status.assert_not_called()

    def test_returns_executions_in_list_mode(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_execution_status.return_value = (
            ExecutionStatus(
                executions=[
                    Execution(
                        name="DailyScheduledETL_testorg_20260730T080000Z",
                        status="SUCCEEDED",
                    )
                ]
            )
        )
        result = DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info()
        assert result is not None
        assert result.executions is not None
        self.assertEqual(
            result.executions[0].name,
            "DailyScheduledETL_testorg_20260730T080000Z"
        )

    def test_latest_mode_can_return_none(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_execution_status.return_value = None
        result = DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info(
            mode=DailyRun.GetDailyRunExecutionMode.LATEST
        )
        self.assertIsNone(result)


@patch("comotion.dash.DailyRunApi")
class TestStartExecution(unittest.TestCase):

    def test_calls_start_operation(self, mock_api_class):
        mock_api_class.return_value.start_daily_run_execution.return_value = (
            StartExecutionResponse(started=True)
        )
        DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()
        mock_api_class.return_value.start_daily_run_execution.assert_called_once_with()

    def test_conflict_returns_payload_instead_of_raising(self, mock_api_class):
        running_payload = StartExecutionResponse(
            started=False,
            message=(
                "Daily ETL pipeline is already running for this client; "
                "no execution started."
            ),
            runningExecution=RunningExecution(
                name="DailyScheduledETL_testorg_20260730T080000Z",
                status="RUNNING",
            ),
        )
        mock_api_class.return_value.start_daily_run_execution.side_effect = (
            ConflictException(status=409, reason="Conflict", data=running_payload)
        )

        result = DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()

        self.assertFalse(result.started)
        self.assertEqual(
            result.running_execution.name,
            "DailyScheduledETL_testorg_20260730T080000Z",
        )

    def test_started_payload_on_success(self, mock_api_class):
        mock_api_class.return_value.start_daily_run_execution.return_value = (
            StartExecutionResponse(
                started=True, executionName="DailyScheduledETL_testorg_x"
            )
        )
        result = DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()
        self.assertTrue(result.started)
        self.assertEqual(result.execution_name, "DailyScheduledETL_testorg_x")

    def test_other_error_statuses_still_raise(self, mock_api_class):
        mock_api_class.return_value.start_daily_run_execution.side_effect = (
            ServiceException(status=500, reason="Server Error", body="boom")
        )
        with self.assertRaises(ValueError):
            DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()

    def test_verify_false_disables_tls_verification(self, mock_api_class):
        mock_api_class.return_value.start_daily_run_execution.return_value = (
            StartExecutionResponse(started=True)
        )
        DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution(verify=False)
        api_client = mock_api_class.call_args[0][0]
        self.assertFalse(api_client.configuration.verify_ssl)

    def test_verify_path_is_used_as_ca_bundle(self, mock_api_class):
        mock_api_class.return_value.start_daily_run_execution.return_value = (
            StartExecutionResponse(started=True)
        )
        DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution(
            verify="/path/to/ca-bundle.pem"
        )
        api_client = mock_api_class.call_args[0][0]
        self.assertTrue(api_client.configuration.verify_ssl)
        self.assertEqual(
            api_client.configuration.ssl_ca_cert, "/path/to/ca-bundle.pem"
        )


@patch("comotion.dash.DailyRunApi")
class TestUpdateDailyRunEnabled(unittest.TestCase):

    def test_posts_expected_body(self, mock_api_class):
        mock_api_class.return_value.update_daily_run_enabled.return_value = (
            DailyRunEnabled(dailyRun=True)
        )
        DailyRun(make_config(ENABLED_WRITE_CLAIMS)).update_daily_run_enabled(True)
        sent = mock_api_class.return_value.update_daily_run_enabled.call_args[1]
        self.assertEqual(sent["daily_run_enabled"], DailyRunEnabled(dailyRun=True))
        self.assertEqual(sent["daily_run_enabled"].to_dict(), {"dailyRun": True})

    def test_rejects_non_boolean(self, mock_api_class):
        with self.assertRaises(TypeError):
            DailyRun(make_config(ENABLED_WRITE_CLAIMS)).update_daily_run_enabled("yes")
        mock_api_class.return_value.update_daily_run_enabled.assert_not_called()


@patch("comotion.dash.DailyRunApi")
class TestErrorTranslation(unittest.TestCase):
    """The wrapper maps generated exceptions onto the SDK's own exceptions."""

    def test_401_becomes_unauthenticated(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.side_effect = (
            UnauthorizedException(status=401, reason="Unauthorized", body="nope")
        )
        with self.assertRaises(UnAuthenticatedException) as context:
            DailyRun(make_config()).get_daily_run_enabled()
        self.assertIn("dailyrun:enabled:read", str(context.exception))

    def test_403_becomes_unauthenticated(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.side_effect = (
            ForbiddenException(status=403, reason="Forbidden", body="nope")
        )
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config()).get_daily_run_enabled()

    def test_404_becomes_value_error(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.side_effect = (
            ApiException(status=404, reason="Not Found", body="DailyRun not found")
        )
        with self.assertRaises(ValueError):
            DailyRun(make_config()).get_daily_run_enabled()

    def test_transport_failure_becomes_value_error(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.side_effect = (
            OSError("connection reset")
        )
        with self.assertRaises(ValueError) as context:
            DailyRun(make_config()).get_daily_run_enabled()
        self.assertIn("/dailyRun/dailyRun_enabled", str(context.exception))

    def test_conflict_on_other_endpoints_still_raises(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.side_effect = (
            ConflictException(status=409, reason="Conflict", body="unexpected")
        )
        with self.assertRaises(ValueError):
            DailyRun(make_config()).get_daily_run_enabled()


@patch("comotion.dash.DailyRunApi")
class TestTokenHandling(unittest.TestCase):

    def test_token_is_refreshed_before_each_call(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.return_value = (
            DailyRunEnabled(dailyRun=True)
        )
        config = make_config()
        DailyRun(config).get_daily_run_enabled()
        config._check_and_refresh_token.assert_called_once()

    def test_refreshed_token_is_passed_to_the_client(self, mock_api_class):
        mock_api_class.return_value.get_daily_run_enabled.return_value = (
            DailyRunEnabled(dailyRun=True)
        )
        config = make_config()
        refreshed = make_token(FULL_ACCESS_CLAIMS)

        def refresh():
            config.access_token = refreshed

        config._check_and_refresh_token.side_effect = refresh

        DailyRun(config).get_daily_run_enabled()

        api_client = mock_api_class.call_args[0][0]
        self.assertEqual(api_client.configuration.access_token, refreshed)


if __name__ == "__main__":
    unittest.main()
