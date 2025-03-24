from http.server import BaseHTTPRequestHandler, HTTPServer

import base64
import hashlib
import json
import os
import re
import requests
import webbrowser
import jwt

from abc import ABC, abstractmethod

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
            self.state = parsed_qs['state']

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

        try:
            json_response = json.loads(response.text)
        except json.JSONDecodeError:
            self.error = "Trouble getting your security tokens: " + response.text
            return

        if response.status_code != 200:
            if "error" in json_response and "error_description" in json_response:
                self.error = json_response["error_description"]
            else:
                self.error = "Could not get a token for you."
            return


        self.id_token = json_response['id_token']

        self.id_token_decoded = jwt.decode(
            self.id_token,
            options={"verify_signature": False}
        )

        try:
            self.server.como_authenticator.credentials_cache.set_refresh_token(
                self.id_token_decoded['preferred_username'],
                json.loads(str(response.text))['refresh_token'])
        except CredentialsCacheException as e:
            self.error = f"There was a problem saving your credentials: {str(e)}"

    # Handler for the redirect from keycloak
    def do_GET(self):
        self._read_query_parameters(urlparse(self.path).query)
        self._process_code()
        self.send_response(200)
        self.end_headers()
        if self.error is not None:
            myheader = "There was a problem authenticating you"
            issuer_message = self.error
            final_message = "If the issue persists, please get in touch with support"
        else:
            myheader = "Authentication complete for " + self.id_token_decoded['preferred_username']
            issuer_message = f"Authenticated at: {self.id_token_decoded['iss']}"
            final_message = f"Go ahead and close this window, your keys are saved in your computer's credentials manager."
        message="""
        <html>
            <head>
                <title>Comotion Auth</title>
            </head>
            <body>
                <span style="font-family:'Courier New'">
                    <br/>
                    <center>
                        <h1> Comotion Auth </h1>
                        <h2>
                            {myheader}
                        </h2>
                        {issuer_message}
                        <br/>
                        <br/>
                        {final_message}
                    </center>
                </span>
            </body>
        <html>
        """.format(myheader=myheader, issuer_message=issuer_message, final_message=final_message)
        self.wfile.write(bytes(message,"utf-8"))
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


class CredentialsCacheException(Exception):
    """
    CredentialsCacheException Thrown in credential save and retrieve in classes implementing CredentialsCacheInterface
    """
    pass

class CredentialsCacheInterface():
    """
    Interfaced to be implemented in concrete class that executes caching
    of credentials for users

    Any errors in the functions should raise a CredentialsCacheException
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
        try:
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
        except keyring.errors.KeyringError as e:
            raise CredentialsCacheException(e)

class AuthException(Exception):
    """
    Exception thrown by Auth class
    """
    pass

class UnAuthenticatedException(AuthException):
    """
    Exception thrown when credentials are not valid.
    """
    pass

class Auth():
    """
    Class that authenticates the user or application, caches credentials.

    Args:
        orgname (str): The name of the organization.
        issuer (str): The issuer URL for authentication. Defaults to 'https://auth.comotion.us'.
        credentials_cache_class (class): The class used for credential caching. Defaults to KeyringCredentialCache.
        entity_type (str): The type of entity being authenticated (Auth.USER or Auth.APPLICATION). Defaults to Auth.USER.
        application_client_id (str, optional): The client ID for the application on auth.comotion.us. When entity_type is Auth.USER, defaults to `comotion_cli`
        application_client_secret (str, optional): The client secret for the application on auth.comotion.us. Only valid when entity_type is Auth.APPLICATION.
    """

    USER='user'
    """
    Constant for user entity type.
    """
    APPLICATION='application'
    """
    Constant for application entity type.
    """

    def __init__(self,
                 orgname,
                 issuer='https://auth.comotion.us',
                 credentials_cache_class=None,
                 entity_type=None,
                 application_client_id=None,
                 application_client_secret=None
                 ):
        
        
        if credentials_cache_class is None:
            credentials_cache_class = KeyringCredentialCache
        

        if entity_type is None or entity_type==Auth.USER:
            entity_type = Auth.USER
            if application_client_secret is not None:
                raise ValueError("when entity_type is Auth.Application, application_client_id and application_client_secret must not be provided")
            if application_client_id is None:
                self.application_client_id = "comotion_cli" # default to comotion_cli if Auth.Application

        elif entity_type==Auth.APPLICATION:
            if application_client_id is None or application_client_secret is None:
                raise ValueError("when entity_type is Auth.Application, application_client_id and application_client_secret must be provided")
            self.application_client_id = application_client_id
            self.application_client_secret = application_client_secret

        else:
            raise ValueError("entity_type must be either Auth.USER or Auth.APPLICATION")

        

        self.issuer = issuer
        self.orgname = orgname
        self.entity_type = entity_type
        self.auth_endpoint = "%s/auth/realms/%s/protocol/openid-connect/auth" % (issuer,orgname) # noqa
        self.token_endpoint = "%s/auth/realms/%s/protocol/openid-connect/token" % (issuer,orgname) # noqa
        self.logout_endpoint = "%s/auth/realms/%s/protocol/openid-connect/logout" % (issuer,orgname) # noqa
        self.delegated_endpoint = "%s/auth/realms/%s/account" % (issuer,orgname) # noqa
        self.refresh_token = None

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
        """
        used by the CLI to run a user authentication process using the auth code flow with auth.comotion.us

        Note that the handle_request function (part of the OIDCServer class) saves the key to an appropriate key manager
        """
        import logging

        logging.captureWarnings(True)
        logging.getLogger().setLevel(logging.DEBUG)
        try:
            state = str(uuid.uuid4())
            pkce = PKCE.generate_pkce()
            # Create a web server and define the handler to manage the incoming request
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

    
    def get_access_token(self):
        """
        Retrieve an access token from the auth provider.

        This method interacts with the authentication provider to retrieve an
        access token. The access token is not cached and must be retrieved
        each time this method is called. The method handles both user and
        application entity types, using the appropriate authentication mechanism
        for each.

        Returns:
            str: The access token retrieved from the auth provider.

        Raises:
            UnAuthenticatedException: If there is an error retrieving the access token
                                      from the auth provider.
        """
        try: 
            if self.entity_type == Auth.USER:
                refresh_token = self.credentials_cache.get_refresh_token()
                payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.application_client_id
                }
            else:
                payload = {
                    "grant_type": "client_credentials",
                    "client_id": self.application_client_id,
                    "client_secret": self.application_client_secret
                }

            response = requests.post(
                self.token_endpoint,
                data=payload
            )

            if response.status_code == requests.codes.ok:
                return json.loads(str(response.text))['access_token']
            else:
                json_response = json.loads(str(response.text))
                if 'error' in json_response:
                    if json_response['error'] == 'invalid_grant':
                        raise UnAuthenticatedException("Your credentials are not valid. Run `comotion authenticate` to refresh your credentials.")
                    else:
                        raise UnAuthenticatedException("There was a problem with the request: " + json_response.get('error_description', "unknown system error. This is what the system is returning: " + response.text) + f" ({json_response['error']})")
                else:
                    raise UnAuthenticatedException("unknown system error. This is what the system is returning: " + response.text)
        except json.JSONDecodeError as e:
            raise UnAuthenticatedException(f"There was a strange response from the server: '{response.text}' ({e.msg})")
        except requests.RequestException as e:
            raise UnAuthenticatedException(f"Request failed: {e}")