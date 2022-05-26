import io
import requests
import csv
import time
from typing import Union, Callable
from os.path import join
import pandas as pd
import logging
import cx_Oracle
import sqlalchemy
from datetime import datetime
from tqdm import tqdm
from comotion import Auth
from comotion import comodash_api_client_lowlevel
from comodash_api_client_lowlevel.comodash_api import queries_api
from comodash_api_client_lowlevel.model.query_text import QueryText
from urllib3.exceptions import IncompleteRead
from urllib3.response import HTTPResponse
from comodash_api_client_lowlevel.model.query import Query as QueryInfo

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
            access_token=auth.get_access_token()
        )

        # comodash_api_client_lowlevel.Configuration.set_default(config)


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
            self.query_api_instance = queries_api.QueriesApi(api_client)
            if query_id:
                query_info = self.query_api_instance.get_query(query_id)
                self.query_id = query_id
                self.query_text = query_info.query
            elif query_text:
                self.query_text = query_text
                query_text_model = QueryText(query=query_text)
                query_id_model = self.query_api_instance.run_query(query_text_model) # noqa
                self.query_id = query_id_model['query_id']
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
        return self.query_api_instance.get_query(self.query_id)

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

                with query.get_csv_for_streaming().stream() as stream:
                  for chunk in stream:
                      # do somthing with chunk
                      # chunk is a byte array ``
        """

        response = self.query_api_instance.download_csv(
            query_id=self.query_id,
            _preload_content=False)
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
        encoding=encoding
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

    print('Initializing complete. Starting the upload...')

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
