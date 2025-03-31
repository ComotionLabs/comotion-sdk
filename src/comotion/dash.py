import io
import os
import json
import requests
import csv
import time
from typing import Union, Callable, List, Optional, Dict, Any
from os.path import join, basename, isdir, isfile, splitext
from os import listdir
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import logging
import boto3
import awswrangler as wr
import re
import uuid
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
from comodash_api_client_lowlevel import Load
from comodash_api_client_lowlevel.models.query import Query as QueryInfo
from comodash_api_client_lowlevel.models.load import Load as LoadInfo
from comodash_api_client_lowlevel.models.file_upload_request import FileUploadRequest
from comodash_api_client_lowlevel.models.file_upload_response import FileUploadResponse
from comodash_api_client_lowlevel.models.load_commit import LoadCommit
from comodash_api_client_lowlevel.models.load import Load
from comodash_api_client_lowlevel.models.query_id import QueryId
from comodash_api_client_lowlevel.rest import ApiException
from concurrent.futures import ThreadPoolExecutor, as_completed
import random 
import string
from inspect import signature, Parameter

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

class Query():
    """
    The query object starts and tracks a query on Comotion Dash.

    Initialising this class runs a query on Comotion Dash and stores the
    resulting query id in `query_id`

    """

    COMPLETED_STATES = ['SUCCEEDED', 'CANCELLED', 'FAILED']
    SUCCEEDED_STATE = 'SUCCEEDED'

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
        
        self.config = config
        with comodash_api_client_lowlevel.ApiClient(self.config) as api_client:
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

    def refresh_api_instance(self):
            auth_token = self.config.auth
            orgname = auth_token.orgname
            entity_type = auth_token.entity_type

            if entity_type == Auth.APPLICATION:
                application_client_id = auth_token.application_client_id
                application_client_secret = auth_token.application_client_secret
            else:
                application_client_id = None
                application_client_secret = None
            
            self.config = DashConfig(
                Auth(
                    orgname=orgname,
                    entity_type=entity_type,
                    application_client_id=application_client_id,
                    application_client_secret=application_client_secret
                )
            )
            with comodash_api_client_lowlevel.ApiClient(self.config) as api_client:
                # Create an instance of the API class with provided parameters
                self.query_api_instance = QueriesApi(api_client)  

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
            self.refresh_api_instance()
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
        self.refresh_api_instance()
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
        self.refresh_api_instance()
        return self.query_api_instance.stop_query(self.query_id)

class Load():
    """
    The Load object starts and tracks a multi-file load to a single lake table on Comotion Dash

    Initialising this class starts a Load on Comotion Dash and stores the
    resulting `load_id`.

    The load then needs to be committed with valid checksums to be pushed to the lake.

    If you wish to work with an existing load, then supply only the `load_id` parameter

    Example of upload with a Load instance:
    
    .. code-block:: python

        load = Load(config = DashConfig(Auth('orgname')), 
                    table_name = 'v1_inforce_policies', 
                    load_as_service_client_id = '0') # Create the load
        
        print(load.load_id) # It can be useful to track these to fix 
        for file, file_key in zip(file_path_list, file_keys): # Upload files with Load object
            load.upload_file(
                data = file,
                file_key = file_key
            )

        load.commit( # Commit the load - this validates the files and pushes to the table_name specified
            check_sum = { # Check that data uploaded matches what you expected before pushing to the lake.  *Also see track_rows_uploaded option
                'sum(face_amount)': 20000,
                'count(distinct policy_number)': 1000
            }
        )

        print(load.get_load_info()) # Run this at any time to get the latest information on the load

    """

    def __init__(
            self,
            config: DashConfig,
            load_type: str = None,
            table_name: str = None,
            load_as_service_client_id: str = None,
            partitions: Optional[List[str]] = None,
            load_id: str = None,
            track_rows_uploaded: bool = None,
            path_to_output_for_dryrun: str = None,
            modify_lambda: Callable = None,
            chunksize: int = None
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
        track_rows_uploaded: bool, optional
            If True, track the number of rows uploaded with the current Load instance.  This can be used to automatically create a checksum on commit (see Load.commit), however is not recommended for 
            large files as this may increase the duration of upload significantly.
        path_to_output_for_dryrun: str, optional
            if specified, no upload will be made to dash, but files
            will be saved to the location specified. This is useful for testing.
        modify_lambda: Callable, optional
            Callable which takes a pandas.DataFrame as the first arg.
            Can be used to add/modify columns in the data before upload to the lake.
        chunksize: int, default 30000
            If a file is uploaded, it will be broken into chunks with chunksize rows before uploading.  Note an index is added to the end of the file key to uniquely identify chunks.
        """
        load_data = locals()
        lowerlevel_load_sig = signature(comodash_api_client_lowlevel.Load)
        lowerlevel_load_keys = [key for key in lowerlevel_load_sig.parameters.keys()]
        if not(isinstance(config, DashConfig)):
            raise TypeError("config must be of type comotion.dash.DashConfig")
        
        self.config = config
        
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
            lowerlevel_load_kwargs = {
                    key: value
                    for key, value in load_data.items()
                    if key in lowerlevel_load_keys
            }

            load = comodash_api_client_lowlevel.Load(**lowerlevel_load_kwargs)

            # Create a new load
            load_id_model = self.load_api_instance.create_load(load)
            self.load_id = load_id_model.load_id

        if track_rows_uploaded:
            self.track_rows_uploaded = track_rows_uploaded
        else:
            self.track_rows_uploaded = False

        self.rows_uploaded = 0
        self.path_to_output_for_dryrun = path_to_output_for_dryrun
        self.modify_lambda = modify_lambda
        if not chunksize:
            self.chunksize = 30000
        else:
            self.chunksize = chunksize

    def refresh_api_instance(self):
        auth_token = self.config.auth
        orgname = auth_token.orgname
        entity_type = auth_token.entity_type

        if entity_type == Auth.APPLICATION:
            application_client_id = auth_token.application_client_id
            application_client_secret = auth_token.application_client_secret
        else:
            application_client_id = None
            application_client_secret = None
        
        self.config = DashConfig(
            Auth(
                orgname=orgname,
                entity_type=entity_type,
                application_client_id=application_client_id,
                application_client_secret=application_client_secret
            )
        )
        with comodash_api_client_lowlevel.ApiClient(self.config) as api_client:
            # Create an instance of the API class with provided parameters
            self.load_api_instance = LoadsApi(api_client)  

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
        self.refresh_api_instance()
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

        self.refresh_api_instance()
        return self.load_api_instance.generate_presigned_url_for_file_upload(self.load_id, file_upload_request=file_upload_request)
        
    def upload_df(self, 
                data: pd.DataFrame, 
                file_key: str = None):
        """
        Uploads a `pandas.DataFrame` as a parquet file to an S3 bucket using a presigned URL.
        If `path_to_output_for_dryrun` is specified for the load, write the file to a local directory instead.
        Before uploading, `modify_lambda` is applied.  Then, column names are forced to be lowercase and spaces are replaced with underscores.
        This is to prevent potential schema issues in the Dash lake.

        Parameters:
        -----------
        data : pandas.DataFrame
            The DataFrame to be uploaded. This should be a pandas.DataFrame object.
        file_key : str, optional
            Optional custom key for the file to be. If not provided, a random file key is created.  See Load.create_file_key().
            This will ensure idempotence. If multiple files are uploaded to the same load with the same `file_key`, only the last one will be pushed to the lake. 
            Must be lowercase and can include underscores.

        Returns:
        --------
        None

        Example:
        --------

        .. code-block:: python

            import pandas as pd
            load = Load(dashconfig)
            df = pd.read_parquet('path/to/file.parquet')
            load.upload_df(data = df, file_key='my_file_id')

        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data should be a valid pandas.DataFrame object")
        
        if not file_key:
            file_key = self.create_file_key()

        if self.modify_lambda:
            self.modify_lambda(data)

        exclude_columns = ['dash$load_id']
        data.columns = [re.sub(r'\s+', '_', column.lower()) for column in data.columns if column not in exclude_columns] # Replace spaces with underscores in column names

        table = pa.Table.from_pandas(data)

        parquet_buffer = io.BytesIO() 
        pq.write_table(table, parquet_buffer)
        parquet_buffer.seek(0)

        file_upload_response = self.generate_presigned_url_for_file_upload(file_key=file_key)

        if not isinstance(file_upload_response, FileUploadResponse):
            raise ValueError("file_upload_response should be a valid instance of FileUploadResponse.")
        else:
            bucket = file_upload_response.bucket
            key = file_upload_response.path 
            # Upload to s3 if not a dry-run
            if not self.path_to_output_for_dryrun:
                s3_file_name = basename(file_upload_response.path)
                
                # Create a session with AWS credentials from the presigned URL
                my_session = boto3.Session(
                    aws_access_key_id=file_upload_response.sts_credentials['AccessKeyId'],
                    aws_secret_access_key=file_upload_response.sts_credentials['SecretAccessKey'],
                    aws_session_token=file_upload_response.sts_credentials['SessionToken']
                )

                # Upload the Parquet buffer as a chunk to S3
                print(f"Uploading to S3: {s3_file_name}")

                upload_reponse = wr.s3.upload(
                    local_file=parquet_buffer, 
                    path=f"s3://{bucket}/{key}", 
                    boto3_session=my_session,
                    use_threads=True
                )
            else:
            # Commence dry run
                local_path = join(self.path_to_output_for_dryrun, f"{basename(key)}.parquet")
                table = pa.Table.from_pandas(data)
                pq.write_table(table, local_path)
                print(f"File written locally to: {local_path}")
                upload_reponse = 'DRYRUN_COMPLETE' # Arbitrary reponse as file write has no return

            if self.track_rows_uploaded:
                # Count the rows in the Parquet file
                rows_uploaded = data.shape[0]
                self.rows_uploaded += rows_uploaded
                print(f"Successfully uploaded {key}: {rows_uploaded} rows")
                print(f"Total rows uploaded for load {self.load_id}: {self.rows_uploaded}")
            else:
                print(f"Upload completed: {key}")

            return upload_reponse
        
    def upload_file(
        self,
        data,
        file_key: str = None,
        use_file_name_as_key: bool = False,
        max_workers: int = None,
        **pd_read_kwargs
    ):
        """
        Uploads a file to the lake table specified in the load, or a local file if `path_to_output_for_dryrun` was specified.
        The file provided is read into a `pandas.DataFrame` using `pd_read_kwargs` with an appropriate pandas function.
        Note an index is added to the end of the file key to uniquely identify chunks uploaded.

        Parameters
        ----------
        data : Any
            The file to be uploaded.  This should be readable by `pandas.read_csv`, `pandas.read_parquet`, `pandas.read_json` or `pandas.read_excel`.
        file_key : str, optional
            A unique key for the file being uploaded. If not provided, a key will be generated.
        use_file_name_as_key : bool, optional
            If True, the file name will be used as the file key. If False, a random key will be generated. Will throw an error when this is True and a file key is provided.
        max_workers : int, optional
            The maximum number of threads to use for concurrent uploads (passed to concurrent.futures.ThreadPoolExecutor)
        **pd_read_kwargs
            Additional keyword arguments to pass to the pandas read function (one of [pd.read_csv, pd.read_parquet, pd.read_json, pd.read_excel]).
            You should not pass the variable pointing to the file here (e.g. filepath_or_buffer in pandas.read_csv), as this is passed in the data parameter.
            Chunksize and nrows should also not be provided as extra parameters.
            If you do not provide dtype, dtype will be determined automatically from the first chunk of data.

        Returns
        -------
        List[Any]
            A list of responses from the load upload API call for each chunk.

        Raises
        ------
        ValueError
            If the file type cannot be determined or if an error occurs during the upload of any chunk.
        """
        responses = []

        invalid_keys = {'filepath_or_buffer', 'chunksize', 'nrows', 'path', 'path_or_buf', 'io'}
        provided_invalid_keys = invalid_keys.intersection(pd_read_kwargs.keys())
        
        if provided_invalid_keys:
            raise ValueError(f"Do not provide the following keys: {', '.join(provided_invalid_keys)}")
        
        print(f"Uploading file: {data}")

        # Reading CSV in chunks, converting each to Parquet, and uploading
        try_functions = [pd.read_csv, pd.read_parquet, pd.read_json, pd.read_excel]

        if file_key and use_file_name_as_key:
            raise Exception("Cannot provide a file key when use_file_name_as_key is True")
        elif file_key and not use_file_name_as_key:
            pass # To be explicit only
        elif use_file_name_as_key and not file_key:
            file_key = os.path.basename(data).split('.')[0] # Remove file extension
        elif not use_file_name_as_key and not file_key:
            file_key = self.create_file_key()
        
        for func in try_functions:
            try:
                func(data, nrows=1, **pd_read_kwargs)
                func_to_use = func
                break
            except:
                pass
        
        if not func_to_use:
            raise ValueError(f"Could not determine file type for datasource with the following file key: {file_key}")
        
        # Determine the dtype for each column if not provided.  
        # Not providing dtype can lead to issues with empty columns and chunks where dtype is determined differently to other chunks.
        if not pd_read_kwargs.get('dtype'):
            sample_df = func_to_use(data, nrows=self.chunksize, **pd_read_kwargs)
            pd_read_kwargs['dtype'] = {col: dtype for col, dtype in sample_df.dtypes.items()}

        try:
            i = 1
            chunk_futures = []
            with ThreadPoolExecutor(max_workers=max_workers) as chunk_ex:  # Using threads for concurrent chunk uploads

                for chunk in func_to_use(data, chunksize=self.chunksize, **pd_read_kwargs):
                    file_key_to_use = file_key + f"_{i}"
                    future = chunk_ex.submit(self.upload_df,
                                            data=chunk,
                                            file_key=file_key_to_use)
                    chunk_futures.append(future)
                    i += 1
                
                for future in as_completed(chunk_futures):
                    responses.append(future.result())

        except Exception as e:
            raise ValueError(f"Error when uploading chunk: {e}")
            
        print("All chunks uploaded successfully")

        return responses
    
    def upload_dash_query(
        self,
        data: Query,
        file_key: str = None,
        max_workers: int = None,
        **pd_read_kwargs
    ):
        """
        Uploads the result of a `dash.Query` object to the specified lake table, or a local file if `path_to_output_for_dryrun` was specified.
        The result is read into a `pandas.DataFrame` and uploaded with the `Load.upload_df()` function.
        Note an index is added to the end of the file key to uniquely identify chunks uploaded.

        Parameters
        ----------
        data : Query
            The Query whose result is to be uploaded.
        file_key : str, optional
            A unique key for the file being uploaded. If not provided, a key will be generated.
        max_workers : int, optional
            The maximum number of threads to use for concurrent uploads (passed to `concurrent.futures.ThreadPoolExecutor`)
        **pd_read_kwargs
            Additional keyword arguments to pass to the pandas function.
            Note that filepath_or_buffer, chunksize and dtype are passed by default and so duplicating those here could cause issues.

        Returns
        -------
        List[Any]
            A list of responses from the load upload API call for each chunk.

        Raises
        ------
        ValueError
            If an error occurs during the upload of any chunk or during the Query.
        """
        responses = []
        
        print(f"Uploading Query with ID: {data.query_id}")

        if not file_key:
            file_key = self.create_file_key()

        invalid_keys = {'filepath_or_buffer', 'chunksize', 'nrows', 'path', 'path_or_buf', 'io'}
        provided_invalid_keys = invalid_keys.intersection(pd_read_kwargs.keys())
        
        if provided_invalid_keys:
            raise ValueError(f"Do not provide the following keys: {', '.join(provided_invalid_keys)}")

        try:
            i = 1
            chunk_futures = []
            data.wait_to_complete()

            print(f"Query completed with state: {data.state()}")

            if data.state() == data.SUCCEEDED_STATE:
                # Determine the dtype for each column if not provided.  
                # Not providing dtype can lead to issues with empty columns and chunks where dtype is determined differently to other chunks.
                if not pd_read_kwargs.get('dtype'):
                    sample_df = pd.read_csv(data.get_csv_for_streaming(), nrows=self.chunksize, **pd_read_kwargs)
                    pd_read_kwargs['dtype'] = {col: dtype for col, dtype in sample_df.dtypes.items()}

                with ThreadPoolExecutor(max_workers=max_workers) as chunk_ex:  # Using threads for concurrent chunk uploads

                    for chunk in pd.read_csv(data.get_csv_for_streaming(), chunksize=self.chunksize, **pd_read_kwargs):
                        file_key_to_use = file_key + f"_{i}"
                        future = chunk_ex.submit(self.upload_df,
                                                data=chunk,
                                                file_key=file_key_to_use)
                        chunk_futures.append(future)
                        i += 1
                    
                    for future in as_completed(chunk_futures):
                        responses.append(future.result())
            else:
                print(f"Query Status: {data.get_query_info().status}")
                print("Please resolve query before re-attempting the upload.")

        except Exception as e:
            raise ValueError(f"Error when uploading chunk: {e}")
            
        print("All chunks uploaded successfully")

        return responses
             
    def commit(self, check_sum: Optional[Dict[str, Union[int, float, str]]] = None):
        """
        Kicks off the commit of the load. A checksum must be provided
        which is checked on the server side to ensure that the data provided
        has integrity.  This is automatically created if you specify `track_rows_uploaded = True` when creating the load.

        Parameters
        ----------
        check_sum : Dict[str, Union[int, float, str]] (optional)
            Checksum data for the files to be committed.
            Checksums must be in the form of a dictionary, with presto / trino expressions
            as the key, and the expected result as the value. 

            A check sum is not required if `track_rows_uploaded` was set to true for the load.  
            This essentially builds the checksum `{'count(*)': nrows_uploads}` and adds it as an extrac checksum.

            Example:

            .. code-block:: python

                {
                    "count(*)" : 53,
                    "sum(my_value)": 123.3
                }
        """
        if not check_sum:
            check_sum = {}
            if not self.track_rows_uploaded:
                raise KeyError("check_sum must be provided for this load as track_rows_uploaded was specified as False.")

        if self.track_rows_uploaded:
            check_sum["count(*)"] = self.rows_uploaded
            
        load_commit = comodash_api_client_lowlevel.LoadCommit(check_sum=check_sum)
        self.refresh_api_instance()
        return self.load_api_instance.commit_load(self.load_id, load_commit)

    def create_file_key(self) -> str:
        """Used to create a random, valid file key with specified length."""
            # Generate a UUID
        raw_uid = str(uuid.uuid4())
        
        # Replace non-alphanumeric characters with underscores
        file_key = 'x_' + re.sub(r'[^a-zA-Z0-9]', '_', raw_uid) # Add initial x_ underscore in case uid starts with integer
        return file_key
    
class DashBulkUploader():
    """
    Class to handle multiple loads with utility functions by leveraging the `Load` class.
    Since a `Load` creates an upload to a lake table, `DashBulkUploader` helps to manage uploads to several lake tables with 1 object.
       
    Example of upload with a `DashBulkUploader` instance:
    
    .. code-block:: python

        auth_token = Auth(orgname = 'my_org_name')

        uploader = DashBulkUploader(auth_token = auth_token)

        # A better use would be to loop through a config to run the following below code repeatedly.  A single upload is shown for demonstration purposes.

        my_lake_table = 'v1_inforce_policies'

        # Create the load in the uploader
        uploader.add_load(
                            table_name = my_lake_table,
                            check_sum = {
                                'count(*)': 50000 
                            }, # Alternatively, provide the track_rows_uploaded arg as true
                            load_as_service_client_id = '0'
                          )

        # Add the relevant datasources to the load. This can point to a directory to upload all contained files
        uploader.add_data_to_load(
                                    table_name = my_lake_table,
                                    data = 'data/inforce_policies'
                                  )
        # View uploads added
        print(uploader.uploads)

        uploader.execute_all_uploads() # Use execute_upload or execute_multiple_uploads if only certain uploads should be kicked off.

        print(uploader.get_load_info()) # View status of uploads.  This also refreshes uploader.uploads 

        # Remove uploads/datasources if you want to re-use the same instance
        uploader.remove_load(table_name = my_lake_table)
    """
    def __init__(self, 
                 auth_token: Auth) -> None:

        self.auth_token = auth_token
        self.pending_load_statuses = ['OPEN']
        self.uploads = {}
    
    def add_load(
        self,
        table_name: str,
        check_sum: Optional[Dict[str, Union[int, float, str]]] = None, 
        modify_lambda: Callable = None,
        load_type: str = 'APPEND_ONLY',
        load_as_service_client_id: str = None,
        partitions: Optional[List[str]] = None,
        track_rows_uploaded: bool = False,
        path_to_output_for_dryrun: str = None,
        chunksize: int = 30000
    ) -> None:
        """
        Creates a new load for a specified lake table. This function initializes the load
        process, ensuring that the table name is in lowercase and that a checksum or row tracking
        is provided for data integrity. Created loads can be fetched using the `DashBulkUploader.uploads` class variable.

        Parameters
        ----------
        table_name : str
            The name of the lake table. Must be in lowercase.
        check_sum : Optional[Dict[str, Union[int, float, str]]]
            Checksum data for the files to be committed. The checksum should be a dictionary
            with Presto/Trino expressions as keys and their expected results as values.
        modify_lambda : Callable, optional
            A lambda function to modify the data before loading.
        load_type : str, default 'APPEND_ONLY'
            The type of load operation. Default is 'APPEND_ONLY'.
        load_as_service_client_id : str, optional
            The service client ID to use for the load. 
            If service_client is not a field in the source data added to the load, this must be provided or the load will fail on commit.
        partitions : Optional[List[str]], optional
            List of partitions for the load to improve query efficiency from the Dash lake.
        track_rows_uploaded : bool, default False
            Whether to track the number of rows uploaded for the load.
        path_to_output_for_dryrun : str, optional
            If specified, no upload will be made to dash, but files
            will be saved to the location specified. This is useful for testing.

        Raises
        ------
        ValueError
            If the table name contains uppercase characters or if a load has already been created for the table.
        KeyError
            If neither `check_sum` nor `track_rows_uploaded` is provided.

        Returns
        -------
        None
        """
        if table_name.lower() != table_name:
            raise ValueError('Only lowercase characters allowed for table_name.')
        
        if table_name in self.uploads:
            raise ValueError(f'A load has been created for the lake table already: {table_name}. Call DashBulkUploader().remove_load({table_name}) if you want to re-start this load.')

        if not check_sum and not track_rows_uploaded:
            raise KeyError("Invalid arguments: Either provide a check_sum value or set track_rows_uploaded to True.")

        if not load_as_service_client_id:
            print("WARNING: Dataset will not upload without specifying load_as_service_client_id option unless there is a column in the data source called service_client_id.")

        print(f"Creating new load for lake table: {table_name}")
        load = Load(
            config=DashConfig(self.auth_token),
            load_type=load_type,
            table_name=table_name,
            load_as_service_client_id=load_as_service_client_id,
            partitions=partitions,
            track_rows_uploaded=track_rows_uploaded,
            path_to_output_for_dryrun=path_to_output_for_dryrun,
            modify_lambda=modify_lambda,
            chunksize=chunksize
        )

        print(f"Load ID: {load.load_id}")
        self.uploads[table_name] = {
            'load': load,
            'data_sources': {}, 
            'check_sum': check_sum,
            'load_status': load.get_load_info().load_status
        }
    
    def add_data_to_load(
        self,
        table_name: str,
        data: Union[str, pd.DataFrame, Query],
        file_key: str = None,
        source_type: str = None,
        dtype: Any = None
    ) -> None:
        """
        Adds data to an existing load for a specified lake table. This function supports adding data
        from various sources including dataframes, directories, and files.

        Parameters
        ----------
        table_name : str
            The name of the lake table to which data will be added.  A load should already be added for this table_name.
        data : Union[str, pd.DataFrame, Query]
            The data to be added. Can be a path to a file or directory, a `pandas.DataFrame` or a `dash.Query`.  See `Load` for how different upload types will be executed.
        file_key : str, optional
            Optional custom key for the file. This will ensure idempotence. Must be lowercase and can include underscores.
            If not provided, a random file key will be generated using `DashBulkUploader.create_file_key()`.
            If a directory is provided as the source of data, `file_key` is ignored and a random file key is generated for each file in the directory.
            If multiple files are uploaded to the same load with the same `file_key`, only the last one will be pushed to the lake. 
        source_type : str, optional
            The type of data source. Can be 'df' for DataFrame, 'dir' for directory, or 'file' for file.
            If not specified, the function will attempt to infer the source type.
            If a directory is provided, loop through the paths in the directory from `listdir()` and add valid files as datasources for the lake table.
        dtype : 
            Will be passed into the pandas read function for the data source.  
            If not provided, dtype will be determined automatically from the first chunk of data.
            This is ignored if the source_type is 'df', as the dtype can be fixed in the dataframe before upload.

        Raises
        ------
        ValueError
            If no existing load is found for the specified table, if the table name is not lowercase,
            or if the source type cannot be identified.
        KeyError
            If neither `check_sum` nor `track_rows_uploaded` is provided.

        Returns
        -------
        None
        """
        upload = self.uploads.get(table_name)
        if not upload:
            raise ValueError(f"No existing load for lake table: {table_name}. First run add_load with the table_name specified before adding data to the load.")
        load = upload['load']

        if not file_key:
            file_key = load.create_file_key()

        if not source_type:
            if isinstance(data, pd.DataFrame):
                source_type = 'df'
            elif isinstance(data, Query):
                source_type = 'query'
            elif isdir(data):
                source_type = 'dir'
            elif isfile(data):
                source_type = 'file'
            else:
                raise ValueError("Source type could not be identified. Please fix datasource or specify the source_type as ['df', 'dir', 'file', 'query']")

        if source_type == 'dir':
            print(f"Unpacking data sources in directory: {data}")

            data_files = [join(data, file_name) for file_name in listdir(data)]
            for file in data_files:
                if not isfile(join(data, file)):
                    print(f"The following path in the directory provided is not a file and so will not be added as a datasource: {file}")
                else:
                    self.add_data_to_load(
                        table_name=table_name, 
                        data=file,
                        file_key=None,  # File keys can't be applied to directories - individual files should be specified if this is required
                        source_type='file',
                        dtype = dtype
                    )
        else:
            
            data_source = {
                'data': data,
                'source_type': source_type,
                'dtype': dtype
            }

            upload['data_sources'][file_key] = data_source
            self.uploads[table_name] = upload

    def remove_data_from_load(
        self,
        table_name,
        file_key
    ):
        """
            Deletes data source with specified file key for table_name from uploads class variable if the load has not been comitted yet.
        """
        if self.uploads[table_name]['load_status'] in self.pending_load_statuses:
            print(f"Removing {file_key} from load for {table_name}")
            self.uploads[table_name]['data_sources'].pop(file_key)
        else:
            raise Exception("Load has already been committed.  First run remove_load and attempt to re-upload.")

    def remove_load(
        self,
        table_name
    ):
        """
            Deletes load for specified table_name from uploads class variable.
        """ 
        print(f"Removing {table_name} from uploads")
        self.uploads.pop(table_name)
    
    def execute_upload(
        self,
        table_name: str,
        max_workers: int = None
    ) -> None:
        """
        Executes the upload process for a specified lake table. This function uses multi-threading
        to upload data sources concurrently and commits the load upon completion.

        Parameters
        ----------
        table_name : str
            The name of the lake table to which data will be uploaded.
        max_workers : int
            The maximum number of threads to use for concurrent uploads (passed to `concurrent.futures.ThreadPoolExecutor`)

        Raises
        ------
        ValueError
            If no existing load is found for the specified table.

        Returns
        -------
        None
        """       
        upload = self.uploads[table_name]
        load = upload['load']
        # Refresh load status
        load_status = load.get_load_info().load_status

        if load_status in self.pending_load_statuses:  # Only perform upload on pending loads
            data_sources = upload['data_sources']
            check_sum = upload['check_sum']
            print(f"Uploading datasources to lake table: {table_name}")

            upload_futures = []

            with ThreadPoolExecutor(max_workers=max_workers) as upload_executor:  # Use multi-threading to speed up uploads
                for file_key, data_source in data_sources.items():
                    data = data_source['data']
                    source_type = data_source['source_type']
                    dtype = data_source['dtype']
                    
                    print(f"Uploading data source with file key: {file_key}")
                    if source_type == 'df':
                        print("Uploading from DataFrame")
                        future = upload_executor.submit(load.upload_df, 
                                                        data=data, 
                                                        file_key=file_key
                                                        )
                    elif source_type == 'query':
                        future = upload_executor.submit(
                                                        load.upload_dash_query,
                                                        data=data,
                                                        file_key=file_key,
                                                        dtype = dtype
                                                        )
                    elif source_type == 'file':
                        future = upload_executor.submit(load.upload_file, 
                                                        data=data,
                                                        file_key=file_key,
                                                        dtype = dtype
                                                        )
                    
                    upload_futures.append(future)

                for f in as_completed(upload_futures):
                    try:
                        f.result()
                    except Exception as e:
                        raise ValueError(f"Error uploading data source: {e}.  Load not yet committed.")
                    # End of uploads 

            # Commit load
            if not load.path_to_output_for_dryrun:
                print(f"All uploads completed. Committing load with the following checksums: {check_sum}")
                load.commit(check_sum=check_sum)
                
            self.uploads[table_name]['load_status'] =  load.get_load_info().load_status

    def execute_multiple_uploads(
        self,
        table_names: List[str],
        max_workers: int = None
    ):
        """
            Uses execute_upload function for each table name in the list provided.
        """
        for table_name in table_names:
            try:
                self.execute_upload(
                    table_name = table_name,
                    max_workers = max_workers
                )
            except Exception as e:
                print(f"Error executing upload to lake table {table_name}: {e}")

    def execute_all_uploads(self):
        """
            Uses execute_upload function for all loads created with the DashBulkUploader.
        """
        table_names = [table_name for table_name in self.uploads.keys()]
        self.execute_multiple_uploads(table_names = table_names)

    def get_load_info(self):
        """
        Retrieves the load information for all loads created. This also updates the load status for each 
        Load created by the `DashBulkUploader`.

        Returns
        -------
        load_info : dict
            A dictionary containing the load information for each table, with table names as keys
            and their respective load statuses as values.

        Raises
        ------
        Exception
            If an error occurs while retrieving the load information for any table, it is caught
            and printed, but the function continues to retrieve the remaining load statuses.
        """
        load_info = {}
        for table_name, upload in self.uploads.items():
            try:
                self.uploads[table_name]['load_status'] = upload['load'].get_load_info().load_status
                load_info[table_name] = upload['load'].get_load_info()
            except Exception as e:
                print(f"Error getting load {self.uploads[table_name]['load'].load_id}: {e}")
                self.uploads[table_name]['load_status'] = f'ERROR: {e}'
                
        return load_info

def v1_upload_csv(
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
        """
        .. Warning::
            This function is deprecated.  Use `read_and_upload_file_to_dash` instead.

        Reads a file and uploads it to Dash.

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
            https://docs.comotion.us/Comotion%20Dash/Analysts/How%20To/Prepare%20Your%20Data%20Model/Y%20Service%20Client%20and%20Row%20Level%20Security.html#service-client-and-row-level-security
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
    file_key: str = None,
    dash_api_key: str = None,
    check_sum: Optional[Dict[str, Union[int, float, str]]] = None,
    encoding: str = 'utf-8',
    chunksize: int = 30000,
    modify_lambda: Callable = None,
    path_to_output_for_dryrun: str = None,
    service_client_id: str = '0',
    partitions: Optional[List[str]] = None,
    load_type: str = 'APPEND_ONLY',
    data_model_version: str = None,
    entity_type: str = Auth.USER,
    application_client_id: str = None,
    application_client_secret: str = None
) -> Union[List[Any], DashBulkUploader]:
    """
    .. Warning::
        This function will be deprecated on 1 December 2025.  Please Migrate and move to the Load/DashBulkUploader class before then.

    Reads a file and uploads it to Dash.

    This function will:
    - Read a CSV file
    - Break it up into multiple CSVs, each with a maximum number of lines defined by `chunksize`
    - Upload them to Dash

    Parameters
    ----------
    file : Union[str, io.FileIO]
        Either a path to the file to be uploaded, or a FileIO stream representing the file to be uploaded.
        Should be an unencrypted, uncompressed CSV file.
    dash_table : str
        Name of the Dash table to upload the file to.
    dash_orgname : str
        Orgname of your Dash instance.
    file_key : str, optional
        A unique key for the file being uploaded. If not provided, a key will be generated.
    dash_api_key : str, optional
        Valid API key for Dash API. Required for v1 data model uploads.
    check_sum : Optional[Dict[str, Union[int, float, str]]], optional
        Checksum data for the files to be committed. The checksum should be a dictionary
        with Presto/Trino expressions as keys and their expected results as values.
    encoding : str, default 'utf-8'
        The encoding of the source file.
    chunksize : int, default 30000
        The maximum number of lines to be included in each file. Note that this should be low enough
        that the zipped file is less than Dash's maximum gzipped file size.
    modify_lambda : Callable, optional
        A callable that receives the pandas DataFrame read from the CSV. Provides the opportunity to modify
        the DataFrame, such as adding a timestamp column.
    path_to_output_for_dryrun : str, optional
        If specified, no upload will be made to Dash, but files will be saved to the location specified.
        This is useful for testing. Multiple files will be created (1 per chunk)
    service_client_id : str, optional
        If specified, specifies the service client for the upload. See the Dash documentation for an explanation
        of the service client.
        https://docs.comotion.us/Comotion%20Dash/Analysts/How%20To/Prepare%20Your%20Data%20Model/Y%20Service%20Client%20and%20Row%20Level%20Security.html#service-client-and-row-level-security
    partitions : Optional[List[str]], optional
        List of partitions for the load.
    load_type : str, default 'APPEND_ONLY'
        The type of load operation. Default is 'APPEND_ONLY'.
    data_model_version : str, optional
        The data model version to use for the upload. If not specified, the function will determine the version.
        If the migration status for the org is 'Completed', v2 is the model version.  Otherwise, v1 is the model version.
        data_model_version only needs be specified in exceptional circumstances where there are issues determining the migration status.
    entity_type : str, default Auth.USER
        The entity type for authentication.  Use Auth.USER if uploading as a user.  Use Auth.APPLICATION if uploading with application credentials.
    application_client_id : str, optional
        The application client ID for authentication.
    application_client_secret : str, optional
        The application client secret for authentication.

    Returns
    -------
    Union[List[Any], DashBulkUploader]
        For v1 data model uploads, returns a list of HTTP responses.
        For v2 data model uploads, returns the DashBulkUploader instance.

    Raises
    ------
    ValueError
        If the API key is not specified for v1 lake upload or if the file type cannot be determined.
    """
    auth_token = Auth(orgname=dash_orgname,
                      entity_type=entity_type,
                      application_client_id=application_client_id,
                      application_client_secret=application_client_secret)
    
    uploader = DashBulkUploader(auth_token=auth_token)
    if not data_model_version or data_model_version not in ['v1', 'v2']:
        print("Determining Data Model Version")
        try:
            config = DashConfig(auth_token)

            # Get migration status
            migration = Migration(config)
            migration_status = migration.status().full_migration_status
            print('Migration Status: ' + migration_status)
            if migration_status in ['Completed', 'Complete']:
                data_model_version = 'v2'
            else:
                data_model_version = 'v1'
        except Exception as e: 
            print(f'Error determining data model version: {e}')
            data_model_version = 'v1'
    else:
        config = DashConfig(auth_token)

    print(f"Uploading to data model {data_model_version}")

    if data_model_version == 'v1':
        if dash_api_key is None:
            raise ValueError("API Key needs to be specified for v1 lake upload.")

        responses = v1_upload_csv(
            file=file,
            dash_table=dash_table,
            dash_orgname=dash_orgname,
            dash_api_key=dash_api_key,
            encoding=encoding,
            chunksize=chunksize,
            modify_lambda=modify_lambda,
            path_to_output_for_dryrun=path_to_output_for_dryrun,
            service_client_id=service_client_id
        )
        return responses
    
    elif data_model_version == 'v2':
        track_rows_uploaded = not check_sum
            
        uploader.add_load(
            table_name=dash_table,
            check_sum=check_sum, 
            modify_lambda=modify_lambda,
            load_type=load_type,
            load_as_service_client_id=service_client_id,
            partitions=partitions,
            track_rows_uploaded=track_rows_uploaded,
            path_to_output_for_dryrun=path_to_output_for_dryrun,
            chunksize=chunksize
        )
        
        uploader.add_data_to_load(
            table_name=dash_table,
            data=file,
            file_key=file_key
        )

        uploader.execute_upload(table_name=dash_table)

        return uploader


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
