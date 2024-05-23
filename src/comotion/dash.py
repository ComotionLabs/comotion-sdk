import io
import os
import json
import requests
import csv
import time
from typing import Union, Callable, List, Optional, Dict
from os.path import join
import pandas as pd
import logging

try:
    import cx_Oracle
    import sqlalchemy
    from tqdm import tqdm
except ImportError:
    pass
from datetime import datetime, timedelta
from comotion import Auth
import comodash_api_client_lowlevel
from comodash_api_client_lowlevel import QueriesApi, LoadsApi, MigrationsApi
from comodash_api_client_lowlevel.models.query_text import QueryText
from urllib3.exceptions import IncompleteRead
from urllib3.response import HTTPResponse
from comodash_api_client_lowlevel.models.query import Query as QueryInfo
from comodash_api_client_lowlevel.models.load import Load as LoadInfo
from comodash_api_client_lowlevel.models.file_upload_request import FileUploadRequest
from comodash_api_client_lowlevel.models.file_upload_response import FileUploadResponse
from comodash_api_client_lowlevel.models.load_commit import LoadCommit
from comodash_api_client_lowlevel.models.load import Load
from comodash_api_client_lowlevel.models.query_id import QueryId
from comodash_api_client_lowlevel.rest import ApiException



class DashConfig(comodash_api_client_lowlevel.Configuration):
    """
    Object containing configuration information for Dash API

    Attributes
    ----------
    auth : comotion.Auth
        comotion.Auth object holding information about authentication
    """

    def __init__(self, auth: Auth):
        if not(isinstance(auth, Auth)):
            raise TypeError("auth must be of type comotion.Auth")

        self.auth = auth

        super().__init__(
            host='https://%s.api.comodash.io/v2' % (auth.orgname),
            access_token=None
        )

        # comodash_api_client_lowlevel.Configuration.set_default(config)

    def _check_and_refresh_token(self):
        """
        checks whether the access token is still valid otherwise refreshes it
        """
        import jwt
        # If there's no token, get one
        if not self.access_token:
            self.access_token = self.auth.get_access_token()
            return

        # Decode the token payload without verification (unsafe for actual use, see below)
        try:
            payload = jwt.decode(self.access_token, options={"verify_signature": False})

            # Get the current time and expiration time from the token
            now = datetime.utcnow()
            exp = datetime.fromtimestamp(payload['exp'])

            # If the token has expired, refresh it
            if now >= (exp - timedelta(seconds=30)):
                self.access_token = self.auth.get_access_token()

        except jwt.ExpiredSignatureError:
            # If the token is expired, refresh it
            self.access_token = self.auth.get_access_token()
        except jwt.DecodeError as e:
            # Handle cases for invalid token
            self.access_token = self.auth.get_access_token()
        except KeyError:
            # Handle cases for tokens with unexpected payload
            self.access_token = self.auth.get_access_token()

    
    def auth_settings(self):
        """Gets Auth Settings dict for api client.

        :return: The Auth Settings information dict.
        """
        # This overrides the lowlevel configuration object to allow for automatic refresh of access token

        self._check_and_refresh_token()
        return super().auth_settings()

class Load():
    """
    The Load object starts and tracks a multi-file load on Comotion Dash

    Initialising this class starts a Load on Comotion Dash and stores the
    resulting load_id in `load_id`

    If you wish to work with an existing load, then simply supply load_id parameter

    @TODO Outline of how to use this class to upload a file here.
    """

    def __init__(
            self,
            config: DashConfig,
            load_type: str = None,
            table_name: str = None,
            load_as_service_client_id: str = None,
            partitions: Optional[List[str]] = None,
            load_id: str = None
    ):
        """
        Parameters
        ----------

        config : DashConfig
            Object of type DashConfig including configuration details.
        load_type : str
            Load Type, initially only APPEND_ONLY supported. APPEND_ONLY means that data is appended to the lake table.
        table_name : str
            Name of lake table to be created and / or uploaded to.
        load_as_service_client_id : str, optional
            If provided, the upload is performed as if run by the service_client specified.
        partitions : list[str], optional
            Only applies if table does not already exist and is created. The created table will have these partitions. This must be a list of iceberg compatible partitions. Note that any load can only allow for up to 100 partitions, otherwise it will error out. If the table already exists, then this is ignored.
        load_id : str, optional
            In the case where you want to work with an existing load on dash, supply this parameter, and no other parameter (other than config) will be required.
        """
        load_data = locals()
        if not(isinstance(config, DashConfig)):
            raise TypeError("config must be of type comotion.dash.DashConfig")
        
        with comodash_api_client_lowlevel.ApiClient(config) as api_client:
            # Create an instance of the API class with provided parameters
            self.load_api_instance = LoadsApi(api_client)

            if (load_id is not None):
                # if load_id provided, then initialise this object with the provided load_id
                self.load_id = load_id
                for key,value in load_data.items():
                    if key not in  ['load_id', 'config', 'self']:
                        if value is not None:
                            raise TypeError("if load_id is supplied, then only the config parameter and no others should be supplied.")
            else:
                # Enter a context with an instance of the API client
                del load_data['config']
                del load_data['self']
                del load_data['load_id']
                load = comodash_api_client_lowlevel.Load(**load_data)

                # Create a new load
                load_id_model = self.load_api_instance.create_load(load)
                self.load_id = load_id_model.load_id

    def get_load_info(self) -> LoadInfo:
        """Gets the state of the load

        Returns
        -------
        LoadInfo
            Model containing all the load info, with the following attributes
            
            `load_status`
                Status of the load, one of OPEN, PROCESSING, FAIL or SUCCESS
            `error_type`
                Type of error if the load status is FAIL.
            `error_messages`
                Detailed error messages if the load status is FAIL.

        """
        return self.load_api_instance.get_load(self.load_id)

    def generate_presigned_url_for_file_upload(self, file_key: str = None) -> FileUploadResponse:
        """
        Generates presigned URLs and STS credentials for a new file upload.

        Parameters
        ----------
        file_key : str, optional
            Optional custom key for the file. This will ensure idempotence.
            If multiple files are uploaded to the same load with the same file_key,
            only the last one will be loaded. Must be lowercase and can include underscores.

        Returns
        -------
        FileUploadResponse
            Model containing all the relevant credentials to be able to upload a file to S3 as part of the load. This includes the following attributes:

            - presigned_url : str
                Presigned URL data for S3 file upload. The file can be posted to this endpoint using any AWS S3 compatible toolset.
                Temporary credentials are included in the URL, so no other credentials are required.
            - sts_credentials : dict
                Alternatively to the presigned_url, these Temporary AWS STS credentials can be used to upload the file to the location specified by `path` and `bucket`.
                This is required for various advanced toolsets, including AWS Wrangler.
            - path : str
                Path of the file in the S3 bucket. See the description of `sts_credentials`.
            - bucket : str
                Name of the S3 bucket. See the description of `sts_credentials`.

        """
        file_upload_request = FileUploadRequest()
        if file_key:
            file_upload_request = FileUploadRequest(file_key=file_key)

        return self.load_api_instance.generate_presigned_url_for_file_upload(self.load_id, file_upload_request=file_upload_request)
        
    def commit(self, check_sum: Dict[str, Union[int, float, str]]):
        """
        Kicks off the commit of the load. A checksum must be provided
        which is checked on the server side to ensure that the data provided
        has integrity.  You can then use the `get_load_info` function to see
        when it is successful.

        Parameters
        ----------
        check_sum : Dict[str, Union[int, float, str]]
            Checksum data for the files to be committed.
            Checksums must be in the form of a dictionary, with presto / trino expressions
            as the key, and the expected result as the value. 
            At least one is required
            Example:

            .. code-block:: python

                {
                    "count(*)" : 53,
                    "sum(my_value)": 123.3
                }
        """
        load_commit = comodash_api_client_lowlevel.LoadCommit(check_sum=check_sum)
        return self.load_api_instance.commit_load(self.load_id, load_commit)


class Query():
    """
    The query object starts and tracks a query on Comotion Dash.

    Initialising this class runs a query on Comotion Dash and stores the
    resulting query id in `query_id`

    """

    COMPLETED_STATES = ['SUCCEEDED', 'CANCELLED', 'FAILED']

    def __init__(
        self,
        config: DashConfig,
        query_text: str = None,
        query_id: str = None
    ):
        """
        Parameters
        ----------
        query_text : str
            sql of the query to run
        config : DashConfig
            Object of type DashConfig including configuration details
        query_id : str, optional
            Query id of existing query.  If not provided, then a new query will be started on Dash

        Raises
        ------
        TypeError
            If config is not of type DashConfig

        ValueError
            if one of query_id or query_text is not provided

        """

        if not(isinstance(config, DashConfig)):
            raise TypeError("config must be of type comotion.dash.DashConfig")

        with comodash_api_client_lowlevel.ApiClient(config) as api_client:
            self.query_api_instance = QueriesApi(api_client)
            if query_id:
                # query_info = self.query_api_instance.get_query(query_id)
                self.query_id = query_id
                # self.query_text = query_info.query
            elif query_text:
                self.query_text = query_text
                query_text_model = QueryText(query=query_text)
                try:
                    query_id_model = self.query_api_instance.run_query(query_text_model) # noqa
                except comodash_api_client_lowlevel.exceptions.BadRequestException as exp:
                    raise ValueError(json.loads(exp.body)['message'])
                    
                self.query_id = query_id_model.query_id
            else:
                raise ValueError("One of query_id or query_text must be provided")

    def get_query_info(self) -> QueryInfo:
        """Gets the state of the query.

        Returns
        -------
        QueryInfo
            Model containing all query info, with the following attributes

            `query`
                query sql
            `query_id`
                query_id of query
            `status`
                `completion_date_time`
                    GMT Completion Time
                `state`
                    Current state of query. One of QUEUED,RUNNING,SUCCEEDED,FAILED,CANCELLED
                `stateChangeReason`
                    info about reason for state change (generally failure)
                submission_date_time`
                    GMT submission time

        """
        try:
            return self.query_api_instance.get_query(self.query_id)
        except comodash_api_client_lowlevel.exceptions.NotFoundException as exp:
            raise ValueError("query_id cannot be found")

    def state(self) -> str:
        """Gets the state of the query.

        Returns
        -------
        str
            One of QUEUED,RUNNING,SUCCEEDED,FAILED,CANCELLED
        """
        return self.get_query_info().status.state

    def is_complete(self) -> bool:
        """Indicates whether the query is in a final state.
        This means it has either succeeded, failed or been cancelled.

        Returns
        -------
        bool
            Whether query complete
        """
        return self.state() in Query.COMPLETED_STATES

    def wait_to_complete(self) -> bool:
        """Blocks until query is in a complete state

        Returns
        -------
        str
            Final state, one of 'SUCCEEDED', 'CANCELLED', 'FAILED'
        """

        while True:
            query_info = self.get_query_info()
            if query_info.status.state in Query.COMPLETED_STATES:
                return query_info
            time.sleep(5)

    def query_id(self) -> str:
        """Returns query id for this query
        """
        return self.query_id

    def get_csv_for_streaming(self) -> HTTPResponse:
        """ Returns a ``urllib3.response.HTTPResponse`` object that can be used for streaming
            This allows use of the downloaded file without having to save
            it to local storage.

            Be sure to use ``.release_conn()`` when completed to ensure that the
            connection is released

            This can be achieved using the `with` notation e.g.::

                with query.get_csv_for3_streaming().stream() as stream:
                  for chunk in stream:
                      # do somthing with chunk
                      # chunk is a byte array ``
        """
        response = self.query_api_instance.download_csv_without_preload_content(
            query_id=self.query_id)
        response.autoclose = False
        return response

    def download_csv(self, output_file_path, fail_if_exists=False):
        """Download csv of results and check that the total file size is correct

        Parameters
        ----------
        output_file_path : File path
            Path of the file to output to
        fail_if_exists : bool, optional
            If true, then will fail if the target file name already/
            Defaults to false.

        Raises
        ------
        IncompleteRead
            If only part of the file is downloaded, this is raised
        """

        with self.get_csv_for_streaming() as response:
            write_mode = "wb"
            if fail_if_exists:
                write_mode = "xb"
            with io.open(output_file_path, write_mode) as f:
                size = 0
                content_length = (response.getheader('Content-Length'))
                for chunk in response.stream(1048576):
                    size = size + len(chunk)
                    f.write(chunk)
                if (response.tell() != int(content_length)):
                    raise IncompleteRead(
                        response.tell(),
                        int(content_length) - response.tell()
                    )

    def stop(self):
        """ Stop the query"""
        return self.query_api_instance.stop_query(self.query_id)


def upload_csv_to_dash(
    dash_orgname: str, # noqa
    dash_api_key: str,
    dash_table: str,
    csv_gz_stream: io.FileIO,
    service_client_id: str = '0'
) -> requests.Response:
    """Uploads csv gzipped stream to Dash

    Expects a csv gzipped stream to upload to dash.

    Args:
        dash_orgname (str): Dash organisation name for dash instance
        dash_api_key (str): Valid API key for the organisation instance
        dash_table (str): Table name to upload to

        csv_gz_stream (io.FileIO): Description

    Returns:
        requests.Response: response from dash api

    Raises:
        HTTPError: If one is raised by the call
    """

    url = "https://api.comodash.io/v1/data-input-file"

    headers = {
        'Content-Type': 'application/gzip',
        'service_client_id': service_client_id,
        'x-api-key': dash_api_key,
        'org-name': dash_orgname,
        'table-name': dash_table
    }

    dash_response = requests.request(
        "POST",
        url,
        headers=headers,
        data=csv_gz_stream.getbuffer()
    )

    dash_response.raise_for_status()

    return dash_response


def create_gzipped_csv_stream_from_df(df: pd.DataFrame) -> io.BytesIO:
    """Returns a gzipped, utf-8 csv file bytestream from a pandas dataframe

    Useful to help upload dataframes to dash

    It does not break file up, so be sure to apply a maximise chunksize
    to the dataframe before applying - otherwise dash max file limits will
    cause an error

    Parameters
    ----------
    df : pd.DataFrame
        Dateframe to be turned into bytestream

    Returns
    -------
    io.BytesIO
        The Bytestream

    """

    csv_stream = io.BytesIO()
    df.to_csv(
        csv_stream,
        compression="gzip",
        encoding="utf-8",
        index=False,
        quoting=csv.QUOTE_NONNUMERIC
    )

    return csv_stream


def read_and_upload_file_to_dash(
    file: Union[str, io.FileIO],
    dash_table: str,
    dash_orgname: str,
    dash_api_key: str,
    encoding: str = 'utf-8',
    chunksize: int = 30000,
    modify_lambda: Callable = None,
    path_to_output_for_dryrun: str = None,
    service_client_id: str = '0'
):
    """Reads a file and uploads to dash.

    This function will:
    - Read a csv file
    - Break it up into multiple csv's
    - each with a maximum number of lines defined by chunksize
    - upload them to dash

    Parameters
    ----------
    file : Union[str, io.FileIO]
        Either a path to the file to be uploaded,
        or a FileIO stream representing the file to be uploaded
        Should be an unencrypted, uncompressed CSV file
    dash_table: str
        name of Dash table to upload the file to
    dash_orgname: str
        orgname of your Dash instance
    dash_api_key: str
        valid api key for Dash API
    encoding: str
        the encoding of the source file.  defaults to utf-8.
    chunksize: int
        (optional)
        the maximum number of lines to be included in each file.
        Note that this should be low enough that the zipped file is less
        than Dash maximum gzipped file size. Defaults to 30000.
    modify_lambda:
        (optional)
        a callable that recieves the pandas dataframe read from the
        csv.  Gives the opportunity to modify - such as adding a timestamp
        column.
        Is not required.
    path_to_output_for_dryrun: str
        (optional)
        if specified, no upload will be made to dash, but files
        will be saved to the location specified. This is useful for
        testing.
        multiple files will be created: [table_name].[i].csv.gz where i
        represents multiple file parts
    service_client_id: str
        (optional)
        if specified, specifies the service client for the upload. See the dash documentation for an explanation of service client.

    Returns
    -------
    List
        List of http responses
    """
    file_reader = pd.read_csv(
        file,
        chunksize=chunksize,
        encoding=encoding,
        dtype=str  # Set all columns to strings.  Dash will still infer the type, but this makes sure it doesnt mess with the contents of the csv before upload
    )

    i = 1
    responses = []
    for file_df in file_reader:

        if modify_lambda is not None:
            modify_lambda(file_df)


        csv_stream = create_gzipped_csv_stream_from_df(file_df)

        if path_to_output_for_dryrun is None:

            response = upload_csv_to_dash(
                dash_orgname=dash_orgname,
                dash_api_key=dash_api_key,
                dash_table=dash_table,
                csv_gz_stream=csv_stream,
                service_client_id=service_client_id
            )

            responses.append(response.text)

        else:
            with open(
                join(
                    path_to_output_for_dryrun,
                    dash_table + "." + str(i) + ".csv.gz"
                ),
                "wb"
            ) as f:
                f.write(csv_stream.getvalue())

        i = i + 1

    return responses

class Migration():
    """
    The Migration object starts and tracks a migration from lake v1 to lake v2. It can only be run once, after which the old lake will be disabled.


    """

    def __init__(
            self,
            config: DashConfig
    ):
        
        if not(isinstance(config, DashConfig)):
            raise TypeError("config must be of type comotion.dash.DashConfig")

        with comodash_api_client_lowlevel.ApiClient(config) as api_client:
            # Create an instance of the API class with provided parameters
            self.migration_api_instance = MigrationsApi(api_client)


    def start(
            self,
            migration_type: str = "FLASH_SCHEMA",
            clear_out_new_lake: bool = False
    ):
        """
        Starts a migration.

        Migrations can take a number of hours to complete. So get a cup of coffee.

        Initialising this class starts the migration on Comotion Dash.  If a migration is already in progress, initialisation will monitor the active load.

        There are two types of migraiton, set by `migration_type`:
        - `FULL_MIGRATION`:  runs a full migration by copying all the data across, updating the insights tables and deactivating data loads to the old lake.
        - `FLASH_SCHEMA`: copies the schema and one line of data per table to the new lake.  this is useful to dev and test ETL scripts

        There is an option to clear out the new lake on migration, set by the boolean parameters `clear_out_new_lake`. This is useful when testing has taken place, and data needs to be cleared.
        If `clear_out_new_lake` is set to False, the migration will fail if there is data in the new lake.

        Parameters
        ----------
        config : DashConfig
            Object of type DashConfig including configuration details
        migration_type : str
            whether to run a full migration ("FULL_MIGRATION") or only copy the schema of the lake across to the new lake ("FLASH_SCHEMA")
        clear_out_new_lake : bool
            whether to clear out the new lake on migration.

        Returns
        -------

        """
        
        if migration_type not in ['FLASH_SCHEMA','FULL_MIGRATION']:
            raise ValueError('`migration_type` must be one of FLASH_SCHEMA or FULL_MIGRATION')

        migration_data = {
            'migration_type': migration_type,
            'clear_out_new_lake': 'CLEAR_OUT' if clear_out_new_lake else 'DO_NOT_CLEAR_OUT'
        }
        
            # Create an instance of the API class with provided parameters
        migration = comodash_api_client_lowlevel.Migration(**migration_data)
        try:
            self.migration_api_instance.start_migration(migration)
        except comodash_api_client_lowlevel.exceptions.BadRequestException as exp:
            raise ValueError(json.loads(exp.body)['message'])
        except comodash_api_client_lowlevel.exceptions.ApiException as e:
            raise ValueError(json.loads(e.body)['message'])
    
    def status(self):
        try:
            migration_status = self.migration_api_instance.get_migration()
            return migration_status
        except comodash_api_client_lowlevel.exceptions.BadRequestException as exp:
            raise ValueError(json.loads(exp.body)['message'])
        except comodash_api_client_lowlevel.exceptions.ApiException as e:
            raise ValueError(json.loads(e.body)['message'])
        

def upload_from_oracle( 
    sql_host: str, 
    sql_port: int, 
    sql_service_name: str, 
    sql_username: str, 
    sql_password: str, 
    sql_query: str,   
    dash_table: str, 
    dash_orgname: str, 
    dash_api_key: str, 
    dtypes: dict = None, 
    include_snapshot: bool = True, 
    export_csvs: bool = True, 
    chunksize: int = 50000, 
    output_path: str = None, 
    sep: str ='\t', 
    max_tries: int = 5 
): 
    """
    Uploads data from a Oracle SQL database object to dash. 

    This function will: 
    - get the total number of rows chunks need for the sql query
    - get chunks of data from the SQL database 
    - upload them to dash 
    - append them to csv output (if specified)
    - save error chunks as csv (if any) 

    Parameters 
    ---------- 
    sql_host: str
        SQL hot e.g. '192.168.0.0.1'
    sql_port: str
        SQL port number e.g 9005
    sql_service_name: str
        SQL service name e.g. 'myservice' 
    sql_username: str 
        SQL username, 
    sql_password: str  
        SQL password, 
    sql_query: str  
        SQL query,  
    dash_table: str 
        name of Dash table to upload the data to 
    dash_orgname: str 
        orgname of your Dash instance 
    dash_api_key: str 
        valid api key for Dash API 
    export_csvs: 
        (optional) 
        If True, data successfully uploaded is exported as csv 
        Defaults to True i.e. output is included 
    dtypes: dict 
        (optional) 
        A dictionary that contains the column name and data type to convert to. 
        Defaults to None i.e. load dataframe columns as they are. 
    chunksize: int 
        (optional) 
        the maximum number of lines to be included in each file. 
        Note that this should be low enough that the zipped file is less 
        than Dash maximum gzipped file size. 
        Defaults to 50000. 
    sep: str 
        (optional) 
        Field delimiter for ComoDash table to upload the dataframe to. 
        Defaults to /t. 
    output_path: str 
        (optional) 
        if specified, no output csv are saved in that location. If not, output is place in the same location as the script
        Defaults to None 
    include_snapshot: bool 
        (optional) 
        If True, an additional column 'snapshot_timestamp' will be added to the DataFrame. 
        This column will contain the time that data is loaded in "%Y-%m-%d %H:%M:%S.%f" 
        format in order to help with database management 
        Defaults to True i.e. snapshot_timestamp is included 
    max_tries: int 
        (optional) 
        Maximum number of times to retry if there is an HTTP error 
        Defaults to 5 
    Returns 
    ------- 
    pd.DataFrame 
        DataFrame with errors 
    """ 

    # Initialize data upload  
      
    print("Initializing. This will take a little while..") 
    
    url = "https://api.comodash.io/v1/data-input-file" 

    headers = { 
        'Content-Type': 'application/gzip', 
        'service_client_id': '0', 
        'x-api-key': dash_api_key, 
        'org-name': dash_orgname, 
        'table-name': dash_table 
    } 

    snapshot_timestamp = datetime.now() 

    # Create load id 
    load_id = dash_table + "_" + snapshot_timestamp.strftime("%Y%m%d%H%M") 

    # Create output folder 
    if export_csvs: 
        if output_path: 
            if not os.path.exists(output_path): 
                os.mkdir(output_path) 
    else: 
        output_path = os.getcwd() 

    # Create log file
    log_file = os.path.join(output_path, load_id + ".log") 
    formatter = logging.Formatter( 
        fmt='%(asctime)s - %(name)-12s %(levelname)-8s %(message)s', 
        datefmt='%Y-%m-%d,%H:%M:%S' 
    ) 
    file_handler = logging.FileHandler(log_file) 
    file_handler.setFormatter(formatter)    
    
    # Create logger
    logger = logging.getLogger(__name__) 
    logger.setLevel(logging.INFO) 
    logger.addHandler(file_handler) 

    # Create sqlalchemy engine 
    sql_dsn = cx_Oracle.makedsn(sql_host, sql_port, service_name=sql_service_name) 
    connection_string = 'oracle://{user}:{password}@{dsn}'.format(user=sql_username, password=sql_password, dsn=sql_dsn)
    engine = sqlalchemy.create_engine(connection_string, max_identifier_length=128) 

    # Connect to database 
    with engine.connect() as connection: 

        # Table properties 
        result = connection.execute(sql_query) 
        columns = [col for col in result.keys()] 
        
        # Calculate results length 
        length = connection.execute(f"select count(*) from ({sql_query})").fetchall()[0][0] 

        if length % chunksize == 0: 
            chunk_number = int(length/chunksize) 
        else: 
            chunk_number = int(length/chunksize) + 1 

        print(f"Starting to upload table with {length} rows in {chunk_number} chunks.") 
  
        # Empty list to store chunks that fail to upload 
        error_chunks = []   

        with open(os.path.join(output_path, load_id + "_success.csv.gz"), "wb") as f: 
            
            for i in tqdm(range(chunk_number)): 

                # Get data chunk
                chunk = pd.DataFrame(result.fetchmany(chunksize), columns=columns) 

                # Include snapshort time if include_snapshot == True 
                if include_snapshot: 
                    chunk['snapshot_timestamp'] = snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f") 
                    
                # Change columns format if dtypes is specified 
                if dtypes: 
                    chunk = chunk.astype(dtype=dtypes) 

                # Create gz_stream 
                csv_stream = io.BytesIO() 
            
                chunk.to_csv( 
                    csv_stream, 
                    compression="gzip", 
                    encoding="utf-8", 
                    index=False, 
                    quoting=csv.QUOTE_MINIMAL, 
                    sep=sep 
                ) 

                trial = 1 

                while True: 
                    try: 
                        response = requests.request( 
                            method="POST", 
                            url=url, 
                            headers=headers, 
                            data=csv_stream.getbuffer() 
                        ) 

                        response.raise_for_status() 

                        if response.status_code == 200: 

                            logger.info(response.text) 

                            trial = 1 

                            if export_csvs:                        
                                f.write(csv_stream.getvalue()) 

                            break 
                    except: 

                        if trial >= max_tries: 

                            logger.info(response.text) 

                            error_chunks.append(chunk) 

                            trial = 1 

                            break 

                        else: 
                            logger.info(response.text) 

                            if export_csvs:                        
                                f.write(csv_stream.getvalue()) 
                            trial += 1 

    print(f"Data uploaded with {len(error_chunks)} error files") 

    # Combine error chunks and export them as csv 

    if len(error_chunks) > 0: 

        print("Exporting errors...") 
        
        error_df = pd.concat(error_chunks) 

        error_df.to_csv( 
            os.path.join(output_path, load_id + "_fail.csv.gz"), 
            compression="gzip", 
            index=False, 
            sep=sep 
        ) 

        return error_df 

    else: 
        return None
