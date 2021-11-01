import click
import json
import keyring
import requests


class Config(object):
    """
    Config objec that allows config to be shared between multiple actions
    """
    def __init__(self):
        self.orgname = None


# make a decorator the allows for config to be passed to multiple actions
# ensure=True makes sure that config is instantiated on first call
pass_config = click.make_pass_decorator(Config, ensure=True)


def _call_well_known(issuer, orgname):
    return requests.get(
        '%s/auth/realms/%s/.well-known/openid-configuration' % (issuer,orgname)) # noqa: E501


def _validate_orgname(issuer, orgname):
    """
    Validates orgname by calling the well-known endpoint of the auth service.

    If it doesnt exist, then a BadParameter exception will be thrown
    If connection doesnt ecist, then will throw a UsageException
    """
    try:
        # check that auth endpoint exists and is happy
        well_known_response = _call_well_known(issuer, orgname)
        if well_known_response.status_code != requests.codes.ok:
            raise click.BadParameter("%s cannot be found at qa.auth.comotion.us.  Make sure you have the correct orgname" % orgname, param_hint='orgname') # noqa E501

    except requests.exceptions.ConnectionError:
        raise click.UsageError("Struggling to connect to the internet!")


@click.group()
@click.option(
    "-o", "--orgname", "orgname",
    type=str,
    required=True,
    help='unique identifier for your organisation')
@pass_config
def cli(config, orgname):
    """
    Command Line Interface for interacting with the Comotion APIs.
    """
    issuer = 'https://qa.auth.comotion.us'
    _validate_orgname(issuer, orgname)

    click.echo("Running in orgname: %s" % orgname)
    config.orgname = orgname


@cli.command()
@pass_config
def login(config):
    """
    Authenticate the user against the provided orgname.
    """

    click.echo("logging you in.  You may see a popup screen to complete authentication...") # noqa

    import jpype
    import jpype.imports
    from jpype.types import JString

    jpype.startJVM()
    jpype.addClassPath("keycloak_install_jars/*")
    from java.io import ByteArrayInputStream
    keycloak_config = {
        "realm": config.orgname,
        "auth-server-url": "https://qa.auth.comotion.us/auth",
        "ssl-required": "external",
        "resource": "redirect_test",
        "public-client": True,
        "use-resource-role-mappings": False,
        "enable-pkce": True
    }

    keycloak_config_stream = ByteArrayInputStream(
        JString(json.dumps(keycloak_config)).getBytes())
    from org.keycloak.adapters.installed import KeycloakInstalled
    keycloak = KeycloakInstalled(keycloak_config_stream)
    from java.util import Locale
    keycloak.setLocale(Locale.ENGLISH)
    keycloak.login()

    # uses LoginDesktop flow if available, otherwise login manual flow.
    # see https://www.keycloak.org/docs/latest/securing_apps/index.html#_installed_adapter # noqa: E501

    refresh_token = keycloak.getRefreshToken()
    refresh_token_string = str(refresh_token)
    preferred_username = str(keycloak.getIdToken().getPreferredUsername())
    jpype.shutdownJVM()

    token_key = "comotion auth api offline token (qa.auth.comotion.us/auth/realms/%s)" % config.orgname # noqa: E501
    keyring.set_password(
        token_key,
        preferred_username,
        refresh_token_string
    )

    click.echo("login is complete.")
