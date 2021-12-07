# from click.testing import CliRunner
from comotion import cli
# import comotion
from unittest.mock import patch, Mock
import unittest
import requests
import click
from click.testing import CliRunner


class SpecialException(Exception):
    pass


class MyTestCase(unittest.TestCase):

    def test_call_well_known(self):
        """
        test return from call_well_known
        """
        with patch.object(cli, 'requests') as requests:
            with patch.object(requests, 'get', return_value="123") as requests_get: # noqa
                result = (cli._call_well_known('issuer', 'myorgame'))
                requests_get.assert_called_once_with('issuer/auth/realms/myorgame/.well-known/openid-configuration') # noqa
                assert result == '123'

    def test_call_well_known_exception(self):
        """
        Test that exception is thrown up by call_well_known
        """
        with patch.object(cli, 'requests') as requests:
            with patch.object(requests, 'get') as get_method:
                get_method.side_effect = SpecialException
                self.assertRaises(
                    SpecialException,
                    cli._call_well_known,
                    'issuer',
                    'orgname')

    def test_validate_orgname_success(self):
        with patch.object(cli, '_call_well_known') as _call_well_known:
            response = Mock(requests.Response)
            response.status_code = 200
            _call_well_known.return_value = response
            cli._validate_orgname('issuer', 'myorg')
            _call_well_known.assert_called_once_with('issuer', 'myorg')
            assert True

    def test_validate_orgname_connectionerror(self):
        with patch.object(cli, '_call_well_known') as _call_well_known:
            _call_well_known.side_effect = requests.exceptions.ConnectionError
            with self.assertRaises(click.UsageError) as ce: # noqa
                cli._validate_orgname('issuer', 'myorg')
                assert str(ce.exception) == 'Struggling to connect to the internet!' # noqa

