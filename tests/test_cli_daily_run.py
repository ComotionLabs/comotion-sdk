import json
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from comodash_dailyrun_api_client_lowlevel.models.execution import Execution
from comodash_dailyrun_api_client_lowlevel.models.execution_status import ExecutionStatus
from comodash_dailyrun_api_client_lowlevel.models.running_execution import RunningExecution
from comodash_dailyrun_api_client_lowlevel.models.start_execution_response import (
    StartExecutionResponse
)

from comotion.cli import cli
from comotion.dash import DailyRun


class DailyRunCliTestCase(unittest.TestCase):
    """Runs the DailyRun CLI commands with Auth, DashConfig and DailyRun patched."""

    def setUp(self):
        self.runner = CliRunner()

        auth_patcher = patch("comotion.cli.Auth")
        self.mock_auth = auth_patcher.start()
        self.addCleanup(auth_patcher.stop)

        config_patcher = patch("comotion.cli.DashConfig")
        self.mock_dash_config = config_patcher.start()
        self.addCleanup(config_patcher.stop)

        # autospec so a wrong keyword (e.g. enable= instead of enabled=) fails
        # the same way it does against the real class.
        daily_run_patcher = patch("comotion.cli.DailyRun", autospec=True)
        self.mock_daily_run_class = daily_run_patcher.start()
        self.addCleanup(daily_run_patcher.stop)
        self.mock_daily_run_class.GetDailyRunExecutionMode = DailyRun.GetDailyRunExecutionMode
        self.daily_run = self.mock_daily_run_class.return_value

    def invoke(self, *args, **kwargs):
        return self.runner.invoke(cli, ["-o", "testorg", "dash", *args], **kwargs)


class TestDailyRunEnabledCommand(DailyRunCliTestCase):

    def test_prints_flag_as_json(self):
        self.daily_run.get_daily_run_enabled.return_value = True
        result = self.invoke("daily-run-enabled")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(json.loads(result.output), True)

    def test_builds_config_for_org_with_default_dns_suffix(self):
        self.daily_run.get_daily_run_enabled.return_value = False
        self.invoke("daily-run-enabled")
        self.mock_auth.assert_called_once_with("testorg", issuer="https://auth.comotion.us")
        self.mock_dash_config.assert_called_once_with(
            self.mock_auth.return_value, dns_suffix="comodash.io"
        )
        self.mock_daily_run_class.assert_called_once_with(self.mock_dash_config.return_value)


class TestDnsSuffixOption(DailyRunCliTestCase):

    def test_comodash_com_reaches_dash_config(self):
        self.daily_run.get_daily_run_enabled.return_value = True
        result = self.invoke("daily-run-enabled", "--dns-suffix", "comodash.com")
        self.assertEqual(result.exit_code, 0, result.output)
        self.mock_dash_config.assert_called_once_with(
            self.mock_auth.return_value, dns_suffix="comodash.com"
        )

    def test_rejects_non_comotion_domain(self):
        result = self.invoke("daily-run-enabled", "--dns-suffix", "evil.example")
        self.assertEqual(result.exit_code, 2)
        self.assertIn("evil.example", result.output)
        self.mock_dash_config.assert_not_called()
        self.daily_run.get_daily_run_enabled.assert_not_called()

    def test_every_daily_run_command_rejects_bad_suffix(self):
        for command in (
            ["daily-run-enabled"],
            ["update-daily-run-enabled", "--enable"],
            ["daily-run-execution-info"],
            ["start-daily-run-execution", "--yes"],
        ):
            with self.subTest(command=command[0]):
                result = self.invoke(*command, "--dns-suffix", "evil.example")
                self.assertEqual(result.exit_code, 2, result.output)
        self.mock_dash_config.assert_not_called()


class TestUpdateDailyRunEnabledCommand(DailyRunCliTestCase):

    def test_enable(self):
        self.daily_run.update_daily_run_enabled.return_value = True
        result = self.invoke("update-daily-run-enabled", "--enable")
        self.assertEqual(result.exit_code, 0, result.output)
        self.daily_run.update_daily_run_enabled.assert_called_once_with(enabled=True)
        self.assertEqual(json.loads(result.output), True)

    def test_disable(self):
        self.daily_run.update_daily_run_enabled.return_value = False
        result = self.invoke("update-daily-run-enabled", "--disable")
        self.assertEqual(result.exit_code, 0, result.output)
        self.daily_run.update_daily_run_enabled.assert_called_once_with(enabled=False)
        self.assertEqual(json.loads(result.output), False)

    def test_both_flags_last_one_wins(self):
        self.daily_run.update_daily_run_enabled.return_value = False
        result = self.invoke("update-daily-run-enabled", "--enable", "--disable")
        self.assertEqual(result.exit_code, 0, result.output)
        self.daily_run.update_daily_run_enabled.assert_called_once_with(enabled=False)

    def test_neither_flag_is_a_usage_error(self):
        result = self.invoke("update-daily-run-enabled")
        self.assertEqual(result.exit_code, 2)
        self.assertIn("--enable or --disable", result.output)
        self.daily_run.update_daily_run_enabled.assert_not_called()


class TestDailyRunExecutionInfoCommand(DailyRunCliTestCase):

    def test_mode_maps_to_enum(self):
        modes = DailyRun.GetDailyRunExecutionMode
        for cli_mode, enum_mode in (
            ("list", modes.LIST),
            ("latest", modes.LATEST),
            ("last_successful", modes.LAST_SUCCESSFUL),
        ):
            with self.subTest(mode=cli_mode):
                self.daily_run.get_execution_info.reset_mock()
                self.daily_run.get_execution_info.return_value = ExecutionStatus()
                result = self.invoke("daily-run-execution-info", "--mode", cli_mode)
                self.assertEqual(result.exit_code, 0, result.output)
                self.daily_run.get_execution_info.assert_called_once_with(
                    mode=enum_mode, limit=None
                )

    def test_defaults_to_list_mode(self):
        self.daily_run.get_execution_info.return_value = ExecutionStatus()
        self.invoke("daily-run-execution-info")
        self.daily_run.get_execution_info.assert_called_once_with(
            mode=DailyRun.GetDailyRunExecutionMode.LIST, limit=None
        )

    def test_rejects_unknown_mode(self):
        result = self.invoke("daily-run-execution-info", "--mode", "everything")
        self.assertEqual(result.exit_code, 2)
        self.daily_run.get_execution_info.assert_not_called()

    def test_limit_is_passed_through(self):
        self.daily_run.get_execution_info.return_value = ExecutionStatus()
        result = self.invoke("daily-run-execution-info", "--limit", "10")
        self.assertEqual(result.exit_code, 0, result.output)
        self.daily_run.get_execution_info.assert_called_once_with(
            mode=DailyRun.GetDailyRunExecutionMode.LIST, limit=10
        )

    def test_limit_out_of_range_is_rejected(self):
        for limit in ("0", "201"):
            with self.subTest(limit=limit):
                result = self.invoke("daily-run-execution-info", "--limit", limit)
                self.assertEqual(result.exit_code, 2, result.output)
        self.daily_run.get_execution_info.assert_not_called()

    def test_limit_bounds_are_accepted(self):
        self.daily_run.get_execution_info.return_value = ExecutionStatus()
        for limit in ("1", "200"):
            with self.subTest(limit=limit):
                result = self.invoke("daily-run-execution-info", "--limit", limit)
                self.assertEqual(result.exit_code, 0, result.output)

    def test_none_result_prints_null(self):
        self.daily_run.get_execution_info.return_value = None
        result = self.invoke("daily-run-execution-info", "--mode", "latest")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIsNone(json.loads(result.output))

    def test_prints_executions_as_json(self):
        self.daily_run.get_execution_info.return_value = ExecutionStatus(
            executions=[
                Execution(
                    name="DailyScheduledETL_testorg_20261007T080000Z",
                    status="SUCCEEDED",
                    startDate="2026-10-07T08:00:00Z",
                )
            ]
        )
        result = self.invoke("daily-run-execution-info")
        self.assertEqual(result.exit_code, 0, result.output)
        payload = json.loads(result.output)
        self.assertEqual(payload["executions"][0]["status"], "SUCCEEDED")
        self.assertEqual(payload["executions"][0]["startDate"], "2026-10-07T08:00:00Z")


class TestStartDailyRunExecutionCommand(DailyRunCliTestCase):

    def test_answering_no_aborts_without_calling_api(self):
        result = self.invoke("start-daily-run-execution", input="n\n")
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Aborted", result.output)
        self.daily_run.start_execution.assert_not_called()

    def test_answering_yes_starts_execution(self):
        self.daily_run.start_execution.return_value = StartExecutionResponse(
            started=True, executionName="DailyScheduledETL_testorg_20261007T150000Z"
        )
        result = self.invoke("start-daily-run-execution", input="y\n")
        self.assertEqual(result.exit_code, 0, result.output)
        self.daily_run.start_execution.assert_called_once_with()

    def test_yes_flag_skips_prompt_and_prints_json(self):
        self.daily_run.start_execution.return_value = StartExecutionResponse(
            started=True, executionName="DailyScheduledETL_testorg_20261007T150000Z"
        )
        result = self.invoke("start-daily-run-execution", "--yes")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertNotIn("Start a Daily ETL pipeline run?", result.output)
        payload = json.loads(result.output)
        self.assertTrue(payload["started"])
        self.assertEqual(
            payload["executionName"], "DailyScheduledETL_testorg_20261007T150000Z"
        )

    def test_already_running_prints_running_execution(self):
        self.daily_run.start_execution.return_value = StartExecutionResponse(
            started=False,
            message="A Daily ETL pipeline execution is already running.",
            runningExecution=RunningExecution(
                name="DailyScheduledETL_testorg_20261007T140000Z", status="RUNNING"
            ),
        )
        result = self.invoke("start-daily-run-execution", "--yes")
        self.assertEqual(result.exit_code, 0, result.output)
        payload = json.loads(result.output)
        self.assertFalse(payload["started"])
        self.assertEqual(payload["runningExecution"]["status"], "RUNNING")


if __name__ == "__main__":
    unittest.main()
