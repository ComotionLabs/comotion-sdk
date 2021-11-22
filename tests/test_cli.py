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

    def test_login(self):
        """
        Test login process, nmocking all jpype and keyring methods
        A mission because we are using java function and have to mock everything
        Alternative could be to write this in java directly and call it once from python.
        """

        # override import of jpype
        import sys
        jpype = Mock()
        jpypeimports = Mock()
        jpypetypes = Mock()
        keycloakconstructor = Mock()
        keycloakinst = Mock()
        org_keycloak_adapters_installed = Mock()
        javautil = Mock()
        java = Mock()
        javaio = Mock()
        sys.modules['jpype'] = jpype
        sys.modules['jpype.imports'] = jpypeimports
        sys.modules['jpype.types'] = jpypetypes
        sys.modules['org'] = Mock()
        sys.modules['org.keycloak'] = Mock()
        sys.modules['org.keycloak.adapters'] = Mock()
        sys.modules['org.keycloak.adapters.installed'] = org_keycloak_adapters_installed
        org_keycloak_adapters_installed.attach_mock(keycloakconstructor, 'KeycloakInstalled')
        keycloakconstructor.return_value = keycloakinst
        sys.modules['java.util'] = javautil
        sys.modules['java.io'] = javaio
        sys.modules['java'] = java
        with patch.object(jpype, 'addClassPath') as addClassPath:
            with patch.object(jpype, 'startJVM') as startJVM:
                # with patch.object(keycloakinstmodule, 'KeycloakInstalled') as keycloakinst:
                with patch.object(keycloakinst, 'setLocale') as setLocale:
                    with patch.object(keycloakinst, 'login') as login:
                        # with patch.object(cli, 'KeycloakInstalled') as keycloakinst:
                        with patch.object(keycloakinst, 'getRefreshToken') as getrtoken: # noqa
                            rtoken = Mock()
                            getrtoken.return_value = rtoken
                            with patch.object(rtoken, '__str__') as rtokenstring:
                                rtokenstring.return_value = 'myawesomerefreshtoken'
                                with patch.object(keycloakinst, 'getIdToken') as getidtoken: # noqa
                                    idtoken = Mock()
                                    getidtoken.return_value = idtoken
                                    with patch.object(idtoken, 'getPreferredUsername') as pun: # noqa
                                        pun.return_value = 'myawesomename'
                                        with patch.object(jpype, 'shutdownJVM') as shutdownJVM: # noqa
                                            with patch.object(cli, 'keyring') as keyring:
                                                with patch.object(keyring, 'set_password') as set_password:  # noqa
                                                    with patch.object(cli,'_validate_orgname') as _validate_orgname: # noqa
                                                        runner = CliRunner()
                                                        result = runner.invoke(
                                                            cli.cli,
                                                            '--orgname hello login'
                                                        )
                                                        assert result.exit_code == 0
                                                        print(result.stdout)
                                                        startJVM.assert_called_once()
                                                        login.assert_called_once()
                                                        setLocale.assert_called_once()
                                                        # test that config is correct
                                                        assert (str(jpypetypes.mock_calls[0])) == """call.JString('{"realm": "hello", "auth-server-url": "https://auth.comotion.us/auth", "ssl-required": "external", "resource": "redirect_test", "public-client": true, "use-resource-role-mappings": false, "enable-pkce": true}')""" # noqa
                                                        addClassPath.assert_called_once_with("keycloak_install_jars/*") # noqa
                                                        getrtoken.assert_called_once()
                                                        getidtoken.assert_called_once()
                                                        pun.assert_called_once()
                                                        shutdownJVM.assert_called_once()
                                                        set_password.assert_called_once_with(
                                                            "comotion auth api offline token (auth.comotion.us/auth/realms/hello)", # noqa
                                                            "myawesomename",
                                                            "myawesomerefreshtoken"
                                                            )
