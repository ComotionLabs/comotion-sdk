from urllib.parse import urlparse, parse_qs, urlencode
import unittest
from unittest.mock import patch, MagicMock
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import json
import jwt
import uuid
import requests

from comotion.auth import OIDCredirectHandler, OIDCServer, PKCE, Auth, KeyringCredentialCache, UnAuthenticatedException


class TestOIDCredirectHandler(unittest.TestCase):
    
    def setUp(self):
        self.mock_server = MagicMock()
        self.mock_server.pkce = MagicMock()
        self.mock_server.como_authenticator = MagicMock()
        self.mock_server.como_authenticator.token_endpoint = "http://mocked_endpoint"
        self.mock_server.como_authenticator.credentials_cache = MagicMock()

        with patch.object(OIDCredirectHandler, '__init__', lambda x, y, z, s: None):
            self.handler = OIDCredirectHandler(MagicMock(), MagicMock(), self.mock_server)
            self.handler.server = self.mock_server
            self.handler.code = "test_code"
            self.handler.id_token = "test_id_token"
            self.handler.id_token_decoded = {"preferred_username": "test_user", "iss": "test_issuer"}

    def tearDown(self):
        self.mock_server = None
        self.handler = None


    @patch('requests.post')
    @patch('jwt.decode')
    def test_process_code(self, mock_jwt_decode, mock_post):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'id_token': self.handler.id_token,
            'refresh_token': 'test_refresh_token'
        })
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        mock_jwt_decode.return_value = self.handler.id_token_decoded

        self.handler._process_code()

        self.assertEqual(self.handler.id_token, "test_id_token")
        self.assertEqual(self.handler.id_token_decoded['preferred_username'], "test_user")
        self.handler.server.como_authenticator.credentials_cache.set_refresh_token.assert_called_with(
            "test_user", "test_refresh_token"
        )



    @patch('requests.post')
    @patch('jwt.decode')
    def test_process_code_fail(self, mock_jwt_decode, mock_post):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'error_message': 'this is an error message'
        })
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        self.handler._process_code()
        
        mock_jwt_decode.assert_not_called()
        self.handler.server.como_authenticator.credentials_cache.set_refresh_token.assert_not_called()

    def test_read_query_parameters(self):
        self.handler._read_query_parameters("code=test_code&state=test_state")
        self.assertEqual(self.handler.code, ["test_code"])
        self.assertEqual(self.handler.state, ["test_state"])

    @patch('comotion.auth.OIDCredirectHandler._process_code')
    def test_do_GET(self, mock_process_code):
        self.handler.path = "/?code=test_code"
        self.handler.wfile = BytesIO()
        self.handler.send_response = MagicMock()
        self.handler.end_headers = MagicMock()
        self.handler.error = None
        self.handler.do_GET()

        mock_process_code.assert_called_once()
        self.handler.send_response.assert_called_with(200)
        self.handler.end_headers.assert_called_once()
        self.assertIn(b"Authentication complete for test_user", self.handler.wfile.getvalue())

class TestAuth(unittest.TestCase):

    def setUp(self):
        self.auth = Auth(
            orgname="test_org",
            issuer="http://mock_issuer",
            credentials_cache_class=KeyringCredentialCache,
            entity_type=Auth.USER
        )
        self.auth.credentials_cache = MagicMock()
        self.auth.credentials_cache.get_refresh_token.return_value = "test_refresh_token"
        self.auth.application_client_secret = "test_client_secret"

    @patch('requests.post')
    def test_get_access_token_user(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            'access_token': 'test_access_token'
        })
        mock_post.return_value = mock_response

        token = self.auth.get_access_token()
        self.assertEqual(token, 'test_access_token')

    @patch('requests.post')
    def test_get_access_token_application(self, mock_post):
        self.auth.entity_type = Auth.APPLICATION
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            'access_token': 'test_access_token'
        })
        mock_post.return_value = mock_response

        token = self.auth.get_access_token()
        self.assertEqual(token, 'test_access_token')

    @patch('requests.post')
    def test_get_access_token_invalid_grant(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = json.dumps({
            'error': 'invalid_grant'
        })
        mock_post.return_value = mock_response

        with self.assertRaises(UnAuthenticatedException) as context:
            self.auth.get_access_token()

        self.assertIn("Your credentials are not valid", str(context.exception))

    @patch('requests.post')
    def test_get_access_token_other_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = json.dumps({
            'error': 'other_error',
            'error_description': 'A different error occurred'
        })
        mock_post.return_value = mock_response

        with self.assertRaises(UnAuthenticatedException) as context:
            self.auth.get_access_token()

        self.assertIn("There was a problem with the request", str(context.exception))

    @patch('requests.post')
    def test_get_access_token_json_decode_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "invalid_json"
        mock_post.return_value = mock_response

        with self.assertRaises(UnAuthenticatedException) as context:
            self.auth.get_access_token()

        self.assertIn("There was a strange response from the server", str(context.exception))

    @patch('requests.post')
    def test_get_access_token_request_exception(self, mock_post):
        mock_post.side_effect = requests.RequestException("Request failed")

        with self.assertRaises(UnAuthenticatedException) as context:
            self.auth.get_access_token()

        self.assertIn("Request failed", str(context.exception))

    @patch('webbrowser.open')
    @patch('comotion.auth.OIDCServer')
    def test_authenticate(self, mock_oidc_server, mock_webbrowser_open):
        mock_server = MagicMock()
        mock_oidc_server.return_value = mock_server

        with patch.object(OIDCredirectHandler, '__init__', lambda x, y, z, s: None):
            self.auth.authenticate()

            mock_oidc_server.assert_called_once()
            mock_webbrowser_open.assert_called_once()
            mock_server.handle_request.assert_called_once()
            mock_server.server_close.assert_called_once()
            mock_server.socket.close.assert_called_once()

    @patch('uuid.uuid4', return_value=uuid.UUID('12345678123456781234567812345678'))
    @patch('comotion.auth.PKCE.generate_pkce')
    def test_build_auth_url(self, mock_generate_pkce, mock_uuid):
        mock_pkce = MagicMock()
        mock_pkce.get_code_challenge.return_value = "test_code_challenge"
        mock_generate_pkce.return_value = mock_pkce

        state = str(uuid.uuid4())
        pkce = PKCE.generate_pkce()
        redirect_uri = "http://localhost:8080"
        auth_url = self.auth._build_auth_url(redirect_uri, state, pkce)

        expected_url = (
            f"http://mock_issuer/auth/realms/test_org/protocol/openid-connect/auth?"
            f"response_type=code&client_id=comotion_cli&redirect_uri=http%3A%2F%2Flocalhost%3A8080"
            f"&scope=openid&state={state}&code_challenge=test_code_challenge&code_challenge_method=S256"
        )
        self.assertEqual(auth_url, expected_url)

if __name__ == '__main__':
    unittest.main()
