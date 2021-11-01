import click
import json
import keyring


class Config(object):
    """
    Config objec that allows config to be shared between multiple actions
    """
    def __init__(self):
        self.orgname = None


# make a decorator the allows for config to be passed to multiple actions
# ensure=True makes sure that config is instantiated on first call
pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option(
    "-o", "--orgname", "orgname",
    type=str,
    required=True,
    help='unique idenfifier for your organisation')
@pass_config
def cli(config, orgname):
    """
    Command Line Interface for interacting with the Comotion APIs.
    """
    click.echo("Running in orgname: %s" % orgname)
    config.orgname = orgname


@cli.command()
@pass_config
def login(config):
    """
    Authenticate the user against the provided orgname.
    """
    click.echo("authenticating...")

    import jpype
    import jpype.imports
    from jpype.types import JString

    click.echo("starting jvm...")
    jpype.startJVM()
    click.echo("jvm started...")
    import pkg_resources
    # jar_location = pkg_resources.get_resource_filename(
    #     __name__,
    #     "../../jars")
    # click.echo(jar_location)

    jpype.addClassPath(__name__ + "../../jars/*")
    from java.io import ByteArrayInputStream

    # ByteArray = jpype.JArray(jpype.JByte)

    keycloak_config = {
        "realm": config.orgname,
        "auth-server-url": "https://qa.auth.comotion.us/auth",
        "ssl-required": "external",
        "resource": "redirect_test",
        "public-client": True,
        "use-resource-role-mappings": False,
        "enable-pkce": True
    }

    click.echo("config")

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

    #.set_password("comotion auth api latest username",'poc_new',preferred_username) # noqa: E501

    token_key = "comotion auth api offline token (qa.auth.comotion.us/auth/realms/%s)" % orgname # noqa: E501

    keyring.set_password(
        token_key,
        preferred_username,
        refresh_token_string
    )


@cli.command()
@pass_config
def logout(config):
    """
    Remove authentication for the current orgname
    """
    pass
