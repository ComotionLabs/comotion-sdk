from http.server import BaseHTTPRequestHandler, HTTPServer

import base64
import hashlib
import json
import os
import re
import requests
import webbrowser
import jwt

from urllib.parse import urlparse, parse_qs, urlencode
import uuid


class OIDCredirectHandler(BaseHTTPRequestHandler):

    def setup(self):
        self.code = None
        self.error = None
        self.errorDescription = None
        self.state = None
        super(BaseHTTPRequestHandler, self).setup()
        global latest_handled_request
        latest_handled_request = self

    def log_message(self, format, *args):
        """
        Overrider log_message to prevent from logging of requests
        """
        pass

    def _read_query_parameters(self, query_string):
        if query_string == '':
            return

        parsed_qs = parse_qs(query_string)
        if 'code' in parsed_qs:
            self.code = parsed_qs['code']
        if 'error' in parsed_qs:
            self.error = parsed_qs['error']
        if 'error_description' in parsed_qs:
            self.errorDescription = parsed_qs['error_description']
        if 'state' in parsed_qs:
            self.errorDescription = parsed_qs['state']

    def _get_redirect_url(self):
        if (self.error is not None):
            return self.server.delegated_endpoint + "?error=true"
        else:
            query_params = {
                'post_logout_redirect_uri': self.server.como_authenticator.delegated_endpoint, # noqa
                'client_id': 'comotion_cli',
                'id_token_hint': self.id_token
            }

            return self.server.como_authenticator.logout_endpoint + "?" + urlencode(query_params) # noqa

    def _process_code(self):
        payload = {
            "grant_type": "authorization_code",
            "code": self.code,
            "redirect_uri": "http://localhost:%s" % (self.server.server_port),
            "client_id": "comotion_cli",
            "code_verifier": self.server.pkce.get_code_verifier()
        }

        response = requests.post(
            self.server.como_authenticator.token_endpoint,
            data=payload
        )

        self.id_token = json.loads(str(response.text))['id_token']

        id_token_decoded = jwt.decode(
            self.id_token,
            options={"verify_signature": False}
        )

        self.server.como_authenticator.credentials_cache.set_refresh_token(
            id_token_decoded['preferred_username'],
            json.loads(str(response.text))['refresh_token'])

    # Handler for the redirect from keycloak
    def do_GET(self):
        self._read_query_parameters(urlparse(self.path).query)
        self._process_code()
        self.send_response(302)
        self.send_header('Location', self._get_redirect_url())
        self.end_headers()
        return


class OIDCServer(HTTPServer):

    def __init__(self, como_authenticator, pkce):
        self.pkce = pkce
        self.como_authenticator = como_authenticator
        super(HTTPServer, self).__init__(('', 0), OIDCredirectHandler)

class PKCE():

    PKCE_CODE_VERIFIER_MAX_LENGTH = 40
    # https://tools.ietf.org/html/rfc7636#section-4.1

    def __init__(self, code_challenge, code_verifier):
        self.code_challenge = code_challenge
        self.code_verifier = code_verifier

    def get_code_challenge(self):
        return self.code_challenge

    def get_code_verifier(self):
        return self.code_verifier

    @staticmethod
    def generate_pkce():
        code_verifier = base64\
            .urlsafe_b64encode(os.urandom(PKCE.PKCE_CODE_VERIFIER_MAX_LENGTH))\
            .decode('utf-8')
        code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)

        code_challenge = hashlib\
            .sha256(code_verifier.encode('utf-8'))\
            .digest()
        code_challenge = base64\
            .urlsafe_b64encode(code_challenge).\
            decode('utf-8')
        code_challenge = code_challenge\
            .replace('=', '')
        return PKCE(code_challenge, code_verifier)


class CredentialsCacheInterface():
    """
    Interfaced to be implemented in concrete class that executes caching
    of credentials for users
    """

    def __init__(self, issuer, orgname):
        self.issuer = issuer
        self.orgname = orgname

    def get_current_user(self):
        """
        Get latest authenticated user for the issuer and orgname

        Returns:
        str: preferred_username
        """
        pass

    def get_offline_token(self):
        """
        Get offline token for the current user from cache
        """
        pass

    def set_offline_token(self, username, token):
        """
        Set offline token for current user and update current user
        """
        pass


class KeyringCredentialCache(CredentialsCacheInterface):
    """
    Credential cache using the python keyring class.
    Saves to local keyring available on linux, windows and macosx
    """

    def _get_token_key(self):
        return "comotion auth api offline token (%s/auth/realms/%s)" % (self.issuer, self.orgname) # noqa: E501

    def _get_username_key(self):
        return 'comotion auth api latest username (%s)' % (self.issuer)

    def get_current_user(self):
        import keyring
        return keyring.get_password(
            self._get_username_key(),
            self.orgname
        )

    def get_refresh_token(self):
        import keyring
        token_key = self._get_token_key()
        return keyring.get_password(
            token_key,
            self.get_current_user()
        )

    def set_refresh_token(self, username, token):
        import keyring
        # save latest username
        keyring.set_password(
            self._get_username_key(),
            self.orgname,
            username
        )

        keyring.set_password(
            self._get_token_key(),
            username,
            token
        )

class Auth():

    """
    Class that authenticates the user, caches credentials
    """

    def __init__(self,
                 orgname,
                 issuer='https://auth.comotion.us',
                 credentials_cache_class=KeyringCredentialCache):

        self.issuer = issuer
        self.orgname = orgname
        self.auth_endpoint = "%s/auth/realms/%s/protocol/openid-connect/auth" % (issuer,orgname) # noqa
        self.token_endpoint = "%s/auth/realms/%s/protocol/openid-connect/token" % (issuer,orgname) # noqa
        self.logout_endpoint = "%s/auth/realms/%s/protocol/openid-connect/logout" % (issuer,orgname) # noqa
        self.delegated_endpoint = "%s/auth/realms/%s/protocol/openid-connect/delegated" % (issuer,orgname) # noqa
        self.refresh_token = None

        # retrieve refresh token from cache?
        self.access_token = None

        self.credentials_cache = credentials_cache_class(issuer, orgname)

    def _build_auth_url(self, redirect_uri, state, pkce):
        query_params = {
            "response_type": "code",
            "client_id": "comotion_cli",
            "redirect_uri": redirect_uri,
            "scope": "openid",
            "state": state,
            "code_challenge": pkce.get_code_challenge(),
            "code_challenge_method": "S256"
        }

        query_params = "?" + urlencode(query_params)
        return self.auth_endpoint + query_params

    def authenticate(self):
        import logging

        logging.captureWarnings(True)
        logging.getLogger().setLevel(logging.DEBUG)
        try:
            state = str(uuid.uuid4())
            pkce = PKCE.generate_pkce()
            # Create a web server and define the handler to manage the
            # incoming request
            server = OIDCServer(
                self,
                pkce
            )

            redirect_server_address = "http://localhost:%s" % (server.server_port) # noqa

            auth_url = self._build_auth_url(
                redirect_server_address,
                state,
                pkce)

            server.timeout = 180

            webbrowser.open(auth_url)

            # Wait for timeout for one http request
            server.handle_request()

            server.server_close()

        finally:
            server.socket.close()

    # TODO: get, cache and refresh access token

    def get_access_token(self):

        refresh_token = self.credentials_cache.get_refresh_token()

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": "comotion_cli"  # TODO
        }

        response = requests.post(
            self.token_endpoint,
            data=payload
        )

        if response.status_code == requests.codes.ok:
            return json.loads(str(response.text))['access_token']
        else:
            raise Exception("Cannot get new token: " + response.text)
