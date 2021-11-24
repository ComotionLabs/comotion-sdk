import click
import json
import keyring
import requests

from .como_authenticator import ComoAuthenticator, KeyringCredentialCache


class Config(object):
    """
    Config object that allows config to be shared between multiple actions
    """
    def __init__(self):
        self.orgname = None
        self.issuer = 'https://auth.comotion.us'


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
            raise click.BadParameter("%s cannot be found at %s.  Make sure you have the correct orgname" % (orgname,issuer), param_hint='orgname') # noqa E501

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

    # click.echo("Running in orgname: %s" % orgname)
    config.orgname = orgname

    _validate_orgname(config.issuer, config.orgname)


@cli.command()
@pass_config
def authenticate(config):
    """
    Authenticate the user against the provided orgname
    """

    click.echo("logging you in.  You may see a popup screen to complete authentication...") # noqa

    como_authenticator = ComoAuthenticator(
        config.issuer,
        config.orgname,
        KeyringCredentialCache
    )
    como_authenticator.authenticate()


@cli.command()
@pass_config
def get_access_token(config):
    """
    Get an access token for the logged in user
    """

    keyring_cache = KeyringCredentialCache(config.issuer, config.orgname)

    refresh_token = keyring_cache.get_refresh_token()

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": "comotion_cli"
    }

    token_address = "%s/auth/realms/%s/protocol/openid-connect/token" % (config.issuer,config.orgname) # noqa

    response = requests.post(
        token_address,
        data=payload
    )

    if response.status_code == requests.codes.ok:
        click.echo(json.loads(str(response.text))['access_token'])
    else:
        click.echo("There is an error with the response:")
        click.echo(response.text)


@cli.command()
@pass_config
def get_current_user(config):
    """
    Get an id token for the logged in user
    """
    preferred_username = keyring.get_password(
        'comotion auth api latest username',
        config.orgname
    )

    click.echo(preferred_username)
