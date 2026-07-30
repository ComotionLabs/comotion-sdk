import unittest
from unittest.mock import MagicMock, patch

import jwt

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


def make_response(status_code=200, json_payload=None, text=""):
    response = MagicMock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 300
    response.text = text
    if isinstance(json_payload, Exception):
        response.json.side_effect = json_payload
    else:
        response.json.return_value = json_payload
    return response


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


class TestDailyRunScopeSplit(unittest.TestCase):

    @patch("comotion.dash.requests.request")
    def test_execution_read_can_view_execution_status(self, mock_request):
        mock_request.return_value = make_response(json_payload={"executions": []})
        DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info()
        mock_request.assert_called_once()

    @patch("comotion.dash.requests.request")
    def test_execution_write_cannot_view_execution_status(self, mock_request):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).get_execution_info()
        mock_request.assert_not_called()

    @patch("comotion.dash.requests.request")
    def test_execution_read_cannot_start_execution(self, mock_request):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(EXECUTION_READ_CLAIMS)).start_execution()
        mock_request.assert_not_called()

    @patch("comotion.dash.requests.request")
    def test_execution_write_can_start_execution(self, mock_request):
        mock_request.return_value = make_response(json_payload={"started": True})
        DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()
        mock_request.assert_called_once()

    @patch("comotion.dash.requests.request")
    def test_execution_scopes_cannot_read_enabled_flag(self, mock_request):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_daily_run_enabled()
        mock_request.assert_not_called()

    @patch("comotion.dash.requests.request")
    def test_enabled_read_can_read_enabled_flag(self, mock_request):
        mock_request.return_value = make_response(json_payload={"dailyRun": True})
        DailyRun(make_config(ENABLED_READ_CLAIMS)).get_daily_run_enabled()
        mock_request.assert_called_once()

    @patch("comotion.dash.requests.request")
    def test_enabled_write_cannot_read_enabled_flag(self, mock_request):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(ENABLED_WRITE_CLAIMS)).get_daily_run_enabled()
        mock_request.assert_not_called()

    @patch("comotion.dash.requests.request")
    def test_enabled_read_cannot_change_enabled_flag(self, mock_request):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(ENABLED_READ_CLAIMS)).update_daily_run_enabled(True)
        mock_request.assert_not_called()

    @patch("comotion.dash.requests.request")
    def test_enabled_write_can_change_enabled_flag(self, mock_request):
        mock_request.return_value = make_response(json_payload={"dailyRun": True})
        DailyRun(make_config(ENABLED_WRITE_CLAIMS)).update_daily_run_enabled(True)
        mock_request.assert_called_once()

    @patch("comotion.dash.requests.request")
    def test_enabled_scopes_cannot_view_execution_status(self, mock_request):
        with self.assertRaises(UnAuthenticatedException):
            DailyRun(make_config(ENABLED_READ_CLAIMS)).get_execution_info()
        mock_request.assert_not_called()


class TestGetDailyRunEnabled(unittest.TestCase):

    @patch("comotion.dash.requests.request")
    def test_calls_correct_url_and_returns_flag(self, mock_request):
        mock_request.return_value = make_response(json_payload={"dailyRun": True})
        result = DailyRun(make_config()).get_daily_run_enabled()
        self.assertTrue(result)
        args, _ = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertIn("/dailyRun/dailyRun_enabled", args[1])


class TestGetExecutionInfo(unittest.TestCase):

    @patch("comotion.dash.requests.request")
    def test_mode_is_sent_as_query_parameter(self, mock_request):
        mock_request.return_value = make_response(json_payload={"executions": []})
        DailyRun(make_config(EXECUTION_READ_CLAIMS)).get_execution_info(
            mode=DailyRun.GetDailyRunExecutionMode.LATEST
        )
        self.assertEqual(mock_request.call_args[1]["params"], {"mode": "latest"})


class TestStartExecution(unittest.TestCase):

    @patch("comotion.dash.requests.request")
    def test_posts_to_start_execution(self, mock_request):
        mock_request.return_value = make_response(json_payload={"started": True})
        DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()
        args, _ = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertIn("/dailyRun/start_execution", args[1])

    @patch("comotion.dash.requests.request")
    def test_conflict_returns_payload_instead_of_raising(self, mock_request):
        running_payload = {
            "started": False,
            "message": "Daily ETL pipeline is already running for this client; "
                       "no execution started.",
            "runningExecution": {
                "name": "DailyScheduledETL_testorg_20260730T080000Z",
                "status": "RUNNING",
            },
        }
        mock_request.return_value = make_response(
            status_code=409, json_payload=running_payload
        )

        result = DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()

        self.assertFalse(result["started"])
        self.assertEqual(
            result["runningExecution"]["name"],
            "DailyScheduledETL_testorg_20260730T080000Z",
        )

    @patch("comotion.dash.requests.request")
    def test_started_payload_on_success(self, mock_request):
        mock_request.return_value = make_response(
            json_payload={"started": True, "executionName": "DailyScheduledETLV2_testorg_x"}
        )
        result = DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()
        self.assertTrue(result["started"])

    @patch("comotion.dash.requests.request")
    def test_other_error_statuses_still_raise(self, mock_request):
        mock_request.return_value = make_response(status_code=500, text="boom")
        with self.assertRaises(ValueError):
            DailyRun(make_config(EXECUTION_WRITE_CLAIMS)).start_execution()


class TestUpdateDailyRunEnabled(unittest.TestCase):

    @patch("comotion.dash.requests.request")
    def test_posts_expected_body(self, mock_request):
        mock_request.return_value = make_response(json_payload={"dailyRun": True})
        DailyRun(make_config(ENABLED_WRITE_CLAIMS)).update_daily_run_enabled(True)
        self.assertEqual(mock_request.call_args[1]["json"], {"dailyRun": True})


if __name__ == "__main__":
    unittest.main()
