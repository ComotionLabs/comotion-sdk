import click
import json
import requests

from .auth import Auth, KeyringCredentialCache
from comotion.dash import DashConfig
from comotion.auth import Auth
from comotion.dash import Query

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

    except requests.exceptions.ConnectionError as e :
        raise click.UsageError("Struggling to connect to the internet!")


@click.group()
@click.option(
    "-o", "--orgname", "orgname",
    type=str,
    required=True,
    prompt=True,
    help='unique identifier for your organisation')
@pass_config
def cli(config, orgname):
    """
    Command Line Interface for interacting with the Comotion APIs.
    """

    config.orgname = orgname

    _validate_orgname(config.issuer, config.orgname)


@cli.command()
@pass_config
def authenticate(config):
    """
    Authenticate the user against the provided orgname
    """

    click.echo("logging you in.  You may see a popup screen in your default browser to complete authentication...") # noqa

    como_auth = Auth(
        config.orgname,
        config.issuer
    )
    como_auth.authenticate()


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
        click.echo("There is an error with the response:", err=True)
        click.echo(response.text,err=True)


@cli.command()
@pass_config
def get_current_user(config):
    """
    Get an id token for the logged in user
    """

    keyring_cache = KeyringCredentialCache(config.issuer, config.orgname)
    click.echo(keyring_cache.get_current_user())


# Dash cli
@cli.group()
@pass_config
def dash(config):
    """
    CLI for Comotion Dash
    """

    pass


@dash.command()
@click.argument(
    'sql',
    required=True
)
@pass_config
def start_query(config, sql):
    """ Start a query. Takes the sql as an argument """
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    query = Query(query_text=sql, config=config)
    click.echo(query.query_id)


@dash.command()
@click.option(
    '-q', '--query_id',
    required=True,
    help='query_id of query to stop'
)
@pass_config
def stop_query(config, query_id):
    """ Stop a query"""
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    Query(query_id=query_id, config=config)
    click.echo('Query stopped')


@dash.command()
@click.option(
    '-q', '--query_id',
    required=True,
    help='query_id of query'
)
@pass_config
def query_state(config, query_id):
    """Get status of a query.  Takes the query_id as an argument"""
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    query = Query(query_id=query_id, config=config)
    click.echo(query.state())


@dash.command()
@click.argument(
    'sql',
    required=False
)
@click.option(
    '-f', '--file',
    required=True,
    type=click.File(
        mode='wb',
        atomic=True
    ),
    help='file path to output file to.'
)
@click.option(
    '-q', '--query_id',
    help='to download a previously run query, query_id of the query'
)
@pass_config
def download(config, query_id, file, sql):
    """
    Downloads a csv of the result of a query

    To download a previously run query, use --query_id, -q option.

    To run and download a new query provide the sql as an argument i.e. `download "select 1"`
    """
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))

    click.echo("running query...")
    try:
        query = Query(query_id=query_id, query_text=sql, config=config)
    except ValueError:
        raise click.BadParameter(
            'Either --query_id must be supplied or sql for query must be given'
        )

    click.echo("query initiated")

    final_query_info = query.wait_to_complete()

    click.echo("query complete")

    if final_query_info.status.state != 'SUCCEEDED':
        raise click.UsageError(
            "There was a problem running the query: "
            + final_query_info.status.stateChangeReason
        )
    try:
        with query.get_csv_for_streaming() as response:
            f = file
            size = 0
            content_length = (response.getheader('Content-Length'))
            with click.progressbar(
                length=int(content_length),
                label='Downloading to ' + file.name
            ) as bar:
                for chunk in response.stream(524288):
                    size = size + len(chunk)
                    f.write(chunk)
                    bar.update(size)

                if (response.tell() != int(content_length)):
                    raise click.UsageError(
                        "There was a problem downloading the file. The file is incomplete. Please try again."
                    )
            click.echo("finalising file...")
    except Exception as e:
        raise click.UsageError(e)

#wait

# run and download


""" wait_and_download waits for a query to be completed and downloads the result.  Either to filename provided or directly to stdout. """







# input / output to file
