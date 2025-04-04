import click
import json
import requests
import os
from .auth import Auth, KeyringCredentialCache
from comotion.dash import DashConfig
from comotion.auth import Auth
from comotion.dash import Query, Load, Migration
from comotion.auth import UnAuthenticatedException
import comotion

from pydantic import BaseModel, ValidationError

import awswrangler as wr

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    auto_envvar_prefix='COMOTION'
)

class Config(object):
    """
    Config object that allows config to be shared between multiple actions
    """

    def __init__(self):
        self.orgname = None
        self.issuer = None


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

def safe_entry_point():
      """
      this is the initial entrypoint for the cli and handles all uncaught exceptions
      """
      try:
          cli()
      except Exception as e:
          click.echo("Error: "+str(e), err=True)
          import sys
          sys.exit(1)

@click.group(name="comotion",context_settings=CONTEXT_SETTINGS, epilog="Check out our docs at https://docs.comotion.us")
@click.option(
    "-o", "--orgname", "orgname",
    type=str,
    required=True,
    prompt=True,
    help='unique identifier for your organisation')
@click.option(
    "-i", "--issuer", "issuer",
    type=str,
    required=False,
    prompt=False,
    default='https://auth.comotion.us',
    help='override issuer for testing')
@pass_config
def cli(config, orgname, issuer):
    """
    Command Line Interface for interacting with the Comotion APIs.
    """
    config.orgname = orgname
    config.issuer = issuer

    # _validate_orgname(config.issuer, config.orgname)


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
def get_issuer(config):
    """
    Authenticate the user against the provided orgname
    """

    click.echo(config.issuer)


@cli.command()
@pass_config
def get_access_token(config):
    """
    Get an access token for the logged in user
    """

    try:
        como_auth = Auth(
            config.orgname,
            config.issuer
        )
        click.echo(como_auth.get_access_token())
    except UnAuthenticatedException as e:
        raise click.ClickException(e)


@cli.command()
@pass_config
def get_current_user(config):
    """
    Get an id token for the logged in user
    """

    keyring_cache = KeyringCredentialCache(config.issuer, config.orgname)
    click.echo(keyring_cache.get_current_user())


# DASH CLI
    
@cli.group()
@pass_config
def dash(config):
    """
    CLI for Comotion Dash
    """

    pass



# QUERY COMMANDS

@dash.command()
@click.argument(
    'sql',
    required=True
)
@pass_config
def start_query(config, sql):
    """ Start a query. Takes the sql as an argument.  The only output is the query_id.
    
    The an example of how query_id can be saved to a variable as follows:
    
    query_id=$(comotion -opoc2 dash start-query "select 1")
    """
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
    query=Query(query_id=query_id, config=config)
    query.stop()
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
@click.option(
    '-q', '--query_id',
    required=True,
    help='query_id of query'
)
@pass_config
def query_info(config, query_id):
    """Get info about the state of a query.  Takes the query_id as an argument"""
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    query = Query(query_id=query_id, config=config)
    query_info = query.get_query_info()
    result = query_info.status.state
    if (hasattr(query_info.status,'state_change_reason') and query_info.status.state_change_reason is not None):
        result = result + ' - ' + query_info.status.state_change_reason
    click.echo(result)


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

    if query_id == None and sql == None:
        raise click.BadParameter('Either --query_id must be supplied or sql for query must be given')

    click.echo("running query...")
    try:
        query = Query(query_id=query_id, query_text=sql, config=config)
        click.echo("query initiated")
        final_query_info = query.wait_to_complete()
    except ValueError as e:
        raise click.BadParameter(e)

    click.echo("query complete")

    if final_query_info.status.state != 'SUCCEEDED':
        raise click.UsageError(
            "There was a problem running the query: "
            + final_query_info.status.state_change_reason
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
                tell=response.tell()
                if (tell != int(content_length)):
                    raise click.UsageError(
                        "There was a problem downloading the file. The file is incomplete. Please try again."
                    )
            click.echo("finalising file...")
    except Exception as e:
        raise click.UsageError(e)


# LOAD COMMANDS

@dash.command()
@click.option(
    "-t", "--load-type", 
    default="APPEND_ONLY",
    type=click.Choice(['APPEND_ONLY'], case_sensitive=True),
    help="Type of load to create.  Only option currently is APPEND_ONLY.", 
    show_default=True,
    required=False
    )
@click.argument(
    'table_name')
@click.option(
    "-s", "--load-as-service-client", 
    help="If provided, the upload is performed as if run by the service_client specified.",
    type=str,
    required=False)
@click.option(
    "-p","--partitions",
    help="Only applies if table does not already exist, and is created.  The created table will have these iceberg compatible partitions. For multiple parition definitions, this option can be specified more than once.  Maximum 100 partitions allowed per load.",
    type=str,
    multiple=True,
    required=False
)
@pass_config
def create_load(
        config, 
        load_type,
        table_name,
        load_as_service_client,
        partitions
    ):
    """ Create a data upload load for Dash for table TABLE_NAME and returns the new LoadId.  
    Files can be uploaded to a load, and once committed all files will be pushed to the lake in an atomic way.
     This stores the load_id in the COMOTION_DASH_QUERY_ID environment variable for future actions. """
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    load = Load(
        load_type=load_type,
        table_name=table_name,
        load_as_service_client_id=load_as_service_client,
        partitions=partitions,
        config=config)
    click.echo(load.load_id)


@dash.command()
@click.argument('input_file', type=click.Path(exists=True, file_okay=True, readable=True, dir_okay=False, resolve_path=True, allow_dash=True))
@click.option(
    '--load_id','-l',
    help="load_id to upload the file to",
    required=True)
@click.option(
    '--file_key','-k',
    help = "Optional custom key for the file. This will ensure idempontence. If multiple files are uploaded to the same load with the same file_key, only the last one will be loaded. Must be lowercase, can include underscores.",
    required=False
)
@pass_config
def upload_file(
        config, 
        load_id,
        input_file,
        file_key
    ):
    """ Upload a file to a Dash Load. """
    import boto3
    import awswrangler as wr

    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    load = Load(config=config, load_id=load_id)

    if not input_file.lower().endswith('.parquet'):
        raise click.BadParameter("The file must be a parquet file with a parquet extension")
    
    click.echo("getting upload info")
    file_upload_info = None
    if file_key:
        file_upload_info = load.generate_presigned_url_for_file_upload(file_key=file_key)
    else:
        file_upload_info = load.generate_presigned_url_for_file_upload()

    with click.open_file(input_file, 'rb') as local_file:
        click.echo("uploading file")
        my_session = boto3.Session(
            aws_access_key_id=file_upload_info.sts_credentials['AccessKeyId'],
            aws_secret_access_key=file_upload_info.sts_credentials['SecretAccessKey'],
            aws_session_token=file_upload_info.sts_credentials['SessionToken'])
        bucket=file_upload_info.bucket
        key=file_upload_info.path
        wr.s3.upload(
            local_file=local_file, 
            path=f"s3://{bucket}/{key}", 
            boto3_session=my_session,
            use_threads=True
        )
    # @TODO move to SDK

@dash.command()
@click.option(
    "-c", "--check_sum", 
    nargs=2,
    help="Checksum data for the files to be committed.  ", 
    multiple=True,
    required=True
    )
@click.option(
    '--load_id','-l',
    required=True
)
@pass_config
def commit_load(
        config, 
        check_sum,
        load_id
    ):
    """ Kicks off the commit of the load. A checksum must be provided
    which is checked on the server side to ensure that the data provided
    has integrity.  You can then use the `get-load-function` function to see
    when it is successful.
    
    Checksums must be in the form of a dictionary, with presto / trino expressions 
    as the key, and the expected result as the value. At least one is required. 
    
    Example:
    
    comotion -imyorgname dash commit-load --load_id myloadid -c "count(*)" "53" -c "sum(my_value)" "123.3"

    """
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    load = Load(config=config, load_id=load_id)
    check_sum_dict = {}
    for check_sum_expression, check_sum_expected in check_sum:
        # check if duplicates
        if check_sum_expression in check_sum_dict:
            raise click.BadOptionUsage(
                option_name='check_sum',
                message=f"duplicate checksum provided for checksum '{check_sum_expression}'" )
        #transform to dict
        check_sum_dict[check_sum_expression] = check_sum_expected
    load.commit(check_sum=check_sum_dict)
    click.echo("Load committed")

@dash.command()
@click.option(
    '--load_id','-l',
    required=True
)
@pass_config
def get_load_info(
        config, 
        load_id
    ):
    """ Gets the state of the load.  If there is an error, prints out the error message.
    
    The state is printed to StdOut and the errors to StdErr.

    Status can be one of the following:
        OPEN: The load is still open, meaning new files can still be added.
        PROCESSING: The load commit has been initiated and is currently being processed.
        FAIL: There was an issue or error during the load commit.
        SUCCESS: The load has been processed successfully.
    
    This allows you can get the status in the following way:

    load_status=$(comotion dash get-load-info -l myloadid)
    
    And the error messages in this way:

    load_error_messages=$(comotion dash get-load-info -l myloadid 2>&1 > /dev/null)

    y """
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    load = Load(config=config, load_id=load_id)
    load_info = load.get_load_info()
    click.echo(load_info.load_status)
    if load_info.load_status == "FAIL":
        for error_message in load_info.error_messages:
            try:
                click.echo(f"{error_message.error_type}:{error_message.error_message}", err=True)
            except:
                click.echo(f"{error_message}", err=True)

@dash.command()
@click.option(
    '--clear-out-new-lake', '-c',
    is_flag=True,
    default=False
)
@click.option('--full-migration', 'migration_type', flag_value='FULL_MIGRATION',
              default=True)
@click.option('--flash-schema', 'migration_type', flag_value='FLASH_SCHEMA')
@click.confirmation_option(prompt='Are you sure you want to execute the migration?')
@pass_config
def start_migration(
    config,
    clear_out_new_lake,
    migration_type
):
    """ Starts a migration from lake v1 to lake v2. The Full Migration can only be run once, after which the old lake will be disabled.

    Migrations can take a number of hours to complete. So get a cup of coffee.

    Initialising this class starts the migration on Comotion Dash.  If a migration is already in progress, initialisation will monitor the active load.
    """    
    dash_config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    Migration(
        config=dash_config
    ).start(
        migration_type=migration_type,
        clear_out_new_lake=clear_out_new_lake
    )
    
    click.echo("Migration started.  Use the following command to check on the status:")
    click.echo(f"comotion -o{config.orgname} dash migration-status")

@dash.command()
@pass_config
def migration_status(
    config
):
    """ Gets migration status for migration lake v1 to lake v2.

    Migrations can take a number of hours to complete. So get a cup of coffee.

    Initialising this class starts the migration on Comotion Dash.  If a migration is already in progress, initialisation will monitor the active load.
    """    
    config = DashConfig(Auth(config.orgname, issuer=config.issuer))
    migration = Migration(
        config=config
    ).status()


    click.echo(f"Flash schema process: {migration.to_dict().get('flash_schema_status','Not Run')}")
    if "flash_schema_message" in migration.to_dict():
        click.echo(f"Flash schema message: {migration.to_dict().get('flash_schema_message','None')}")
    click.echo(f"Full migration process: {migration.to_dict().get('full_migration_status','Not Run')}")
    if "full_migration_message" in migration.to_dict():
        click.echo(f"Full migration message: {migration.to_dict().get('full_migration_message','None')}")
    




# @TODO 4 (SDK AND CLI) upload to multiple tables for a set file structure /{table_name}/files.  Result must include full output of which passed and which failed.
# @TODO 3 (SDK AND CLI) create upload this filepath - all the files - and wait until fully processed. Must be able to deal with csv and parquet.
            # Must have an option to not wait until fully processed.   Must take a folder path OR  a list of files.
            
# @TODO 2 (SDK and CLI) Convert to parquet and upload.  CSV 

# @TODO 1c (SDK And CLI) "waiter" to wait for processing to finish
            
# @TODO 1 (SDK)  upload a pandas stream   1. as part of a load 2. without having to create a load  3. deal with pandas streams or modin streams or iterator
# @TODO 1b (SDK) upload a file object. specify either csv or parquet. must deal with csv.gz

# @TODO when uploading file without a uid, manufacture one (maybe)

#Done
# @TODO integration tests integration testing from cli down to api call
# @TODO improve auth flow when no user or when password expired. currently nondescript
# # long running auth3



# input / output to file



    
    
#init to initialise your environment with a default orgname