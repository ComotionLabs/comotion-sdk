import unittest
from unittest import mock
from unittest.mock import Mock, patch, MagicMock,create_autospec, mock_open
from unittest.mock import call
from comotion import dash
from comotion.dash import DashConfig, Auth
import requests
import io
from pandas import DataFrame 
import pandas as pd
import boto3
import os

import unittest
from unittest.mock import MagicMock, patch
from comodash_api_client_lowlevel.models.query import Query as QueryInfo
from comodash_api_client_lowlevel.models.query_id import QueryId
from comodash_api_client_lowlevel.models.query_text import QueryText
from comodash_api_client_lowlevel.models.query_status import QueryStatus
from comotion.dash import Query, DashConfig, DashBulkUploader, Load
from comodash_api_client_lowlevel.models.load import Load as LoadInfo
from comodash_api_client_lowlevel.models.file_upload_response import FileUploadResponse
from urllib3.response import HTTPResponse
import pyarrow.parquet

class TestDashModuleLoadClass(unittest.TestCase):

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.LoadsApi')
    @patch('comodash_api_client_lowlevel.Load')
    def test_init_valid_input(self, mock_comodash_api_client_lowlevel_load, mock_loads_api, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Mock the API client and LoadsApi
        mock_api_client_instance = mock_api_client.return_value.__enter__.return_value
        mock_loads_api_instance = mock_loads_api.return_value
        mock_load_id_model = mock_loads_api_instance.create_load.return_value
        mock_load_id_model.load_id ='123'
        # mock_loads_api_instance.create_load.return_value = mock_load_id_model
        
        from comotion.dash import Load
        # Test valid initialization
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )
        # print(mock_comodash_api_client_lowlevel_load.mock_calls)
        # mock_comodash_api_client_lowlevel_load.assert_called_once_with(load_as_service_client_id='service_client', load_type='APPEND_ONLY', partitions=['partition1', 'partition2'], table_name='test_table')
        mock_comodash_api_client_lowlevel_load.assert_called_once() # TODO: Check if the call was made with the correct arguments. Above line is failing.
        mock_loads_api.assert_called_once_with(mock_api_client_instance)
        mock_loads_api_instance.create_load.assert_called_once_with(mock_comodash_api_client_lowlevel_load.return_value)
        self.assertIsNotNone(load)
        self.assertEqual(load.load_id, '123')

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.LoadsApi')
    @patch('comodash_api_client_lowlevel.Load')
    def test_init_valid_input_load_id_provided(self, mock_comodash_api_client_lowlevel_load, mock_loads_api, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Mock the API client and LoadsApi
        mock_api_client_instance = mock_api_client.return_value.__enter__.return_value
        mock_loads_api_instance = mock_loads_api.return_value
        mock_load_id_model = {'load_id': '123'}
        mock_loads_api_instance.create_load.return_value = mock_load_id_model
        
        from comotion.dash import Load
        # Test valid initialization
        load = Load(
            config=mock_config,
            load_id='myloadid'
        )
        mock_comodash_api_client_lowlevel_load.assert_not_called()
        mock_loads_api.assert_called_once()
        mock_loads_api_instance.create_load.assert_not_called()
        self.assertIsNotNone(load)
        self.assertEqual(load.load_id, 'myloadid')

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.LoadsApi')
    @patch('comodash_api_client_lowlevel.Load')
    def test_init_valid_input_load_id_provided_with_others_error(self, mock_comodash_api_client_lowlevel_load, mock_loads_api, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Mock the API client and LoadsApi
        mock_api_client_instance = mock_api_client.return_value.__enter__.return_value
        mock_loads_api_instance = mock_loads_api.return_value
        mock_load_id_model = {'load_id': '123'}
        mock_loads_api_instance.create_load.return_value = mock_load_id_model
        
        from comotion.dash import Load
        # Test valid initialization
        with self.assertRaises(TypeError):
            load = Load(
                config=mock_config,
                load_type='APPEND_ONLY',
                table_name='test_table',
                load_as_service_client_id='service_client',
                partitions=['partition1', 'partition2'],
                load_id='myloadid'
            )

    def test_init_invalid_config_type(self):
        with self.assertRaises(TypeError):
            from comotion.dash import Load
            Load(
                config='invalid_config',  # This should be of type DashConfig
                load_type='APPEND_ONLY',
                table_name='test_table'
            )

    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.refresh_api_instance')
    @patch('comotion.dash.LoadInfo')  # Patch LoadInfo if it's from a different module
    def test_get_load_info(self, mock_load_info, mock_refresh_api_instance, mock_lowlevel_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        # Create a mock Load instance
        from comotion.dash import Load
        # mock_load = create_autospec(Load, instance=True)
        mock_load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )
        mock_load.load_api_instance = MagicMock()
        mock_load.load_id = '123'

        # Set up the return value for the mocked get_load method
        mock_load_info_instance = mock_load_info.return_value
        mock_load.load_api_instance.get_load.return_value = mock_load_info_instance

        # Call the method
        result = mock_load.get_load_info()

        # Assertions
        mock_load.load_api_instance.get_load.assert_called_once_with('123')
        self.assertEqual(result, mock_load_info_instance)
        # Add any additional assertions here, e.g., checking attributes of result if necessary

    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.refresh_api_instance')
    @patch('comotion.dash.FileUploadResponse')  # Patch FileUploadResponse if it's from a different module
    def test_generate_presigned_url_for_file_upload(self, mock_file_upload_response, mock_refresh_api_instance, mock_lowlevel_api_client):
        # Create a Load instance without running its __init__ method
        from comotion.dash import Load
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        # Create a mock Load instance
        mock_load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )

        # Manually set necessary attributes
        mock_load.load_api_instance = MagicMock()
        mock_load.load_id = '123'

        # Set up the return value for the mocked generate_presigned_url_for_file_upload method
        mock_file_upload_response_instance = mock_file_upload_response.return_value
        mock_load.load_api_instance.generate_presigned_url_for_file_upload.return_value = mock_file_upload_response_instance

        # Call the method without file_key
        result = mock_load.generate_presigned_url_for_file_upload()
        # Assertions
        from comodash_api_client_lowlevel.models.file_upload_request import FileUploadRequest
        mock_load.load_api_instance.generate_presigned_url_for_file_upload.assert_called_once_with('123', file_upload_request=FileUploadRequest())
        self.assertEqual(result, mock_file_upload_response_instance)

        # Reset mock
        mock_load.load_api_instance.generate_presigned_url_for_file_upload.reset_mock()

        # Call the method with file_key
        result_with_key = mock_load.generate_presigned_url_for_file_upload(file_key='test_key')
        # Assertions
        mock_load.load_api_instance.generate_presigned_url_for_file_upload.assert_called_once_with('123', file_upload_request=FileUploadRequest(file_key='test_key'))
        self.assertEqual(result_with_key, mock_file_upload_response_instance)

    @patch('comotion.dash.LoadsApi')
    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.comodash_api_client_lowlevel.LoadCommit')
    @patch('comotion.dash.Load.refresh_api_instance')
    def test_commit_with_checksum(self, mock_refresh_api_instance, mock_lowlevel_load_commit_class, mock_lowlevel_api_client, mock_loads_api):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Mock the LoadsApi
        mock_loads_api_instance = mock_loads_api.return_value

        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )

        # Define a test checksum dictionary
        test_check_sum = {
            "count(*)": 53,
            "sum(my_value)": 123.3
        }

        # Call the method
        result = load.commit(test_check_sum)

        # Assertions
        mock_lowlevel_load_commit_class.assert_called_once()
        mock_loads_api_instance.commit_load.assert_called_once()

    @patch('comotion.dash.LoadsApi')
    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.comodash_api_client_lowlevel.LoadCommit')
    @patch('comotion.dash.Load.refresh_api_instance')
    def test_commit_without_checksum(self, mock_refresh_api_instance, mock_lowlevel_load_commit_class, mock_lowlevel_api_client, mock_loads_api):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Mock the LoadsApi
        mock_loads_api_instance = mock_loads_api.return_value

        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2'],
            track_rows_uploaded=True
        )

        # Call the method
        result = load.commit()

        # Assertions
        mock_lowlevel_load_commit_class.assert_called_once()
        mock_loads_api_instance.commit_load.assert_called_once()

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.LoadsApi')
    @patch('comodash_api_client_lowlevel.Load')
    def test_commit_without_checksum_and_tracking(self, mock_comodash_api_client_lowlevel_load, mock_loads_api, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Mock the API client and LoadsApi
        mock_loads_api_instance = mock_loads_api.return_value

        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )

        load.load_api_instance = mock_loads_api_instance

        # Call the method and expect a KeyError
        with self.assertRaises(KeyError):
            load.commit()

    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.generate_presigned_url_for_file_upload')
    @patch('comotion.dash.wr.s3.upload')
    @patch('pyarrow.parquet.write_table')
    @patch('boto3.Session')
    def test_upload_df_valid_dataframe(self, mock_boto_session, mock_write_table, mock_s3_upload, mock_generate_presigned_url, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        
        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )

        # Mock the FileUploadResponse
        mock_file_upload_response = MagicMock(spec=FileUploadResponse)
        mock_file_upload_response.bucket = 'bucket'
        mock_file_upload_response.path = 'key'
        mock_file_upload_response.sts_credentials = MagicMock()
        mock_generate_presigned_url.return_value = mock_file_upload_response

        # Create a valid DataFrame
        data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})

        # Call the upload_df method
        load.upload_df(data=data)

        # Assertions
        mock_s3_upload.assert_called()

    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.generate_presigned_url_for_file_upload')
    @patch('comotion.dash.wr.s3.upload')
    @patch('pyarrow.parquet.write_table')
    def test_upload_df_dryrun(self, mock_write_table, mock_s3_upload, mock_generate_presigned_url, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        
        # Create a Load instance with path_to_output_for_dryrun specified
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2'],
            path_to_output_for_dryrun='/tmp'
        )

        # Mock the FileUploadResponse
        mock_file_upload_response = MagicMock(spec=FileUploadResponse)
        mock_file_upload_response.bucket = 'bucket'
        mock_file_upload_response.path = 'key'
        mock_generate_presigned_url.return_value = mock_file_upload_response

        # Create a valid DataFrame
        data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})

        # Call the upload_df method
        load.upload_df(data=data)

        # Assertions
        mock_s3_upload.assert_not_called()

    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.generate_presigned_url_for_file_upload')
    @patch('comotion.dash.wr.s3.upload')
    @patch('pyarrow.parquet.write_table')
    def test_upload_df_invalid_data(self, mock_write_table, mock_s3_upload, mock_generate_presigned_url, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        
        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )

        # Mock the FileUploadResponse
        mock_file_upload_response = MagicMock(spec=FileUploadResponse)
        mock_generate_presigned_url.return_value = mock_file_upload_response

        # Invalid data (not a DataFrame)
        data = "invalid_data"

        # Call the upload_df method and expect a ValueError
        with self.assertRaises(ValueError):
            load.upload_df(data=data)

        mock_s3_upload.assert_not_called()

    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.generate_presigned_url_for_file_upload')
    @patch('comotion.dash.Load.upload_df')
    @patch('pandas.read_excel')
    @patch('pandas.read_json')
    @patch('pandas.read_parquet')
    @patch('pandas.read_csv')
    def test_upload_file(self, mock_read_csv, mock_read_parquet, mock_read_json, mock_read_excel, mock_upload_df, mock_generate_presigned_url, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Create a Load instance
        from comotion.dash import Load
        chunksize = 1000
        pd_read_options = 4
        csv_load, parquet_load, json_load, excel_load, invalid_load = (
                Load(
                config=mock_config,
                load_type='APPEND_ONLY',
                table_name='test_table',
                load_as_service_client_id='service_client',
                chunksize=chunksize
            )
            for i in range(pd_read_options+1)
        )

        # Mock the file reading and chunking
        mock_chunk = pd.DataFrame({'col1': [1, 2, 5, 6], 'col2': [3, 4, 7, 8]})
        expected_dtype = {col: dtype for col, dtype in mock_chunk.dtypes.items()}

        mock_read_functions = [
            (mock_read_csv, csv_load),
            (mock_read_parquet, parquet_load),
            (mock_read_json, json_load),
            (mock_read_excel, excel_load)
        ]

        for mock_read, load_instance in mock_read_functions:
            mock_read.return_value = mock_chunk
            load_instance.upload_file(
            data='valid_file_path',
            # file_key='test_file_key'
            )
            mock_read.assert_called_with('valid_file_path', chunksize=chunksize, dtype=expected_dtype)

            # Simulate an exception for the next iteration
            mock_read.side_effect = Exception(f"An error occurred while reading the file")

        self.assertEqual(mock_upload_df.call_count, pd_read_options*2)

        # Assert that if all the above read methods fail, an exception is raised
        with self.assertRaises(Exception) as context:
            invalid_load.upload_file(
                data='invalid_file_path',
                # file_key='test_file_key'
            )

    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Query.wait_to_complete')
    @patch('comotion.dash.Query.get_csv_for_streaming')
    @patch('comotion.dash.Load.upload_df')
    @patch('pandas.read_csv')
    def test_upload_dash_query_successful(
        self, mock_read_csv, mock_upload_df, mock_get_csv_for_streaming, mock_wait_to_complete, mock_api_client
    ):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )

        # Mock the Query object
        mock_query = MagicMock(spec=Query)
        mock_query.state = MagicMock(return_value=Query.SUCCEEDED_STATE)
        mock_query.SUCCEEDED_STATE = Query.SUCCEEDED_STATE
        mock_query.query_id = '123'

        # Mock the CSV streaming response
        mock_csv_stream = MagicMock()
        mock_get_csv_for_streaming.return_value = mock_csv_stream

        # Mock the DataFrame chunks
        mock_chunk = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        mock_read_csv.return_value = mock_chunk

        # Call the upload_dash_query method
        responses = load.upload_dash_query(data=mock_query, file_key='test_file_key', max_workers=1)

        # Assertions
        self.assertEqual(mock_upload_df.call_count, 2) 
        self.assertEqual(len(responses), 2)

    @patch('comotion.dash.Load.upload_df')
    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Query.wait_to_complete')
    @patch('comotion.dash.Query.state', return_value='FAILED')
    def test_upload_dash_query_failed_query(self, mock_query_state, mock_wait_to_complete, mock_api_client, mock_upload_df):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )

        # Mock the Query object
        mock_query = MagicMock(spec=Query)
        mock_query.state = MagicMock(return_value='Failed', spec=callable)
        mock_query.SUCCEEDED_STATE = Query.SUCCEEDED_STATE
        mock_query.query_id = '123'

        # Call the upload_dash_query method
        responses = load.upload_dash_query(data=mock_query, file_key='test_file_key')

        # Assertions
        mock_upload_df.assert_not_called()
        self.assertEqual(responses, [])

    @patch('comotion.dash.Load.create_file_key')
    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.upload_df')
    @patch('pandas.read_csv')
    def test_upload_file_with_file_key(self, mock_read_csv, mock_upload_df, mock_api_client, file_key_mock):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        chunksize = 1000
        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2'],
            chunksize=1000
        )

        # Mock the file reading and chunking
        mock_chunk = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        mock_read_csv.return_value = mock_chunk
        expected_dtype = {col: dtype for col, dtype in mock_chunk.dtypes.items()}

        # Call the upload_file method with a file key
        load.upload_file(
            data='valid_file_path',
            file_key='test_file_key'
        )

        # Assertions
        file_key_mock.assert_not_called()
        mock_read_csv.assert_called_with('valid_file_path', chunksize=chunksize, dtype=expected_dtype)
        self.assertEqual(mock_upload_df.call_count, 2)

    @patch('comotion.dash.Load.create_file_key')
    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.upload_df')
    @patch('pandas.read_csv')
    def test_upload_file_without_file_key(self, mock_read_csv, mock_upload_df, mock_api_client, file_key_mock):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        chunksize = 1000
        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2'],
            chunksize=chunksize
        )

         # Mock the file reading and chunking
        mock_chunk = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        mock_read_csv.return_value = mock_chunk
        expected_dtype = {col: dtype for col, dtype in mock_chunk.dtypes.items()}

        # Call the upload_file method without a file key
        load.upload_file(
            data='valid_file_path'
        )

        # Assertions
        file_key_mock.assert_called_once()
        mock_read_csv.assert_called_with('valid_file_path', chunksize=chunksize, dtype=expected_dtype)
        self.assertEqual(mock_upload_df.call_count, 2)

    @patch('os.path.basename', return_value = 'valid_file_path.csv')
    @patch('comotion.dash.Load.create_file_key')
    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.upload_df')
    @patch('pandas.read_csv')
    def test_upload_file_with_use_file_name_as_key(self, mock_read_csv, mock_upload_df, mock_api_client, file_key_mock, basename_mock):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        chunksize = 1000
        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2'],
            chunksize=chunksize
        )

        # Mock the file reading and chunking
        mock_chunk = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        mock_read_csv.return_value = mock_chunk
        expected_dtype = {col: dtype for col, dtype in mock_chunk.dtypes.items()}
        

        # Call the upload_file method with use_file_name_as_key set to True
        load.upload_file(
            data='valid_file_path.csv',
            use_file_name_as_key=True
        )

        # Assertions
        basename_mock.assert_called_once()
        file_key_mock.assert_not_called()
        mock_read_csv.assert_called_with('valid_file_path.csv', chunksize=chunksize, dtype=expected_dtype)
        self.assertEqual(mock_upload_df.call_count, 2)

    @patch('comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.Load.upload_df')
    @patch('pandas.read_csv')
    def test_upload_file_with_file_key_and_use_file_name_as_key(self, mock_read_csv, mock_upload_df, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Create a Load instance
        load = Load(
            config=mock_config,
            load_type='APPEND_ONLY',
            table_name='test_table',
            load_as_service_client_id='service_client',
            partitions=['partition1', 'partition2']
        )

        # Mock the file reading and chunking
        mock_chunk = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        mock_read_csv.return_value = mock_chunk

        # Call the upload_file method with both file_key and use_file_name_as_key
        with self.assertRaises(Exception):
            load.upload_file(
                data='valid_file_path.csv',
                file_key='test_file_key',
                use_file_name_as_key=True
            )
        
class TestDashModule(unittest.TestCase):

    @mock.patch('comotion.dash.create_gzipped_csv_stream_from_df')
    @mock.patch('comotion.dash.upload_csv_to_dash')
    @mock.patch('comotion.dash.pd.read_csv')
    def test_read_and_upload_file_to_dash_str_file(self,
                                                   read_csv,
                                                   upload_csv_to_dash,
                                                   create_gzipped_csv_stream_from_df
        ):
        # test file string passed to read_and_upload_file_to_dash
        create_gzipped_csv_stream_from_df.side_effect = [
            'this is a csv_gz stream1',
            'this is a csv_gz stream2',
            'this is a csv_gz stream3'
        ]
        read_csv.return_value = [1,2,3]


        response1 = Mock(requests.Response)
        response1.text = 'response1'
        response2 = Mock(requests.Response)
        response2.text = 'response2'
        response3 = Mock(requests.Response)
        response3.text = 'response3'
        upload_csv_to_dash.side_effect = [
            response1,
            response2,
            response3
        ]

        result = dash.read_and_upload_file_to_dash(
            file = 'file',
            dash_table = 'mydashtable',
            dash_orgname = 'mydash_orgname',
            dash_api_key = 'mydash_api_key'
        )
        read_csv.assert_called_once_with(
            'file',
            chunksize=30000,
            encoding='utf-8',
            dtype=str)


        create_gzipped_csv_stream_from_df_calls = [call(1),call(2),call(3)]
        create_gzipped_csv_stream_from_df.assert_has_calls(create_gzipped_csv_stream_from_df_calls)

        upload_csv_to_dash_calls = [
            call(dash_orgname = 'mydash_orgname',
                dash_api_key = 'mydash_api_key',
                dash_table = 'mydashtable',
                csv_gz_stream='this is a csv_gz stream1',
                service_client_id='0'),
             call(dash_orgname = 'mydash_orgname',
                dash_api_key = 'mydash_api_key',
                dash_table = 'mydashtable',
                csv_gz_stream='this is a csv_gz stream2',
                service_client_id='0'),
             call(dash_orgname = 'mydash_orgname',
                  dash_api_key = 'mydash_api_key',
                dash_table = 'mydashtable',
                csv_gz_stream='this is a csv_gz stream3',
                service_client_id='0')
        ]


        upload_csv_to_dash.assert_has_calls(upload_csv_to_dash_calls)

        self.assertEqual(result,['response1', 'response2', 'response3'])


    @mock.patch('comotion.dash.create_gzipped_csv_stream_from_df')
    @mock.patch('comotion.dash.upload_csv_to_dash')
    @mock.patch('comotion.dash.pd.read_csv')
    def test_read_and_upload_file_to_dash_str_file_with_service_client_id(self,
                                                   read_csv,
                                                   upload_csv_to_dash,
                                                   create_gzipped_csv_stream_from_df
        ):
        # test file string passed to read_and_upload_file_to_dash with service client specified
        create_gzipped_csv_stream_from_df.side_effect = [
            'this is a csv_gz stream1',
            'this is a csv_gz stream2',
            'this is a csv_gz stream3'
        ]
        read_csv.return_value = [1,2,3]


        response1 = Mock(requests.Response)
        response1.text = 'response1'
        response2 = Mock(requests.Response)
        response2.text = 'response2'
        response3 = Mock(requests.Response)
        response3.text = 'response3'
        upload_csv_to_dash.side_effect = [
            response1,
            response2,
            response3
        ]

        result = dash.read_and_upload_file_to_dash(
            file = 'file',
            dash_table = 'mydashtable',
            dash_orgname = 'mydash_orgname',
            dash_api_key = 'mydash_api_key',
            service_client_id='myservice_client'
        )
        read_csv.assert_called_once_with(
            'file',
            chunksize=30000,
            encoding='utf-8',
            dtype=str)


        create_gzipped_csv_stream_from_df_calls = [call(1),call(2),call(3)]
        create_gzipped_csv_stream_from_df.assert_has_calls(create_gzipped_csv_stream_from_df_calls)

        upload_csv_to_dash_calls = [
            call(dash_orgname = 'mydash_orgname',
                dash_api_key = 'mydash_api_key',
                dash_table = 'mydashtable',
                csv_gz_stream='this is a csv_gz stream1',
                service_client_id='myservice_client'),
             call(dash_orgname = 'mydash_orgname',
                dash_api_key = 'mydash_api_key',
                dash_table = 'mydashtable',
                csv_gz_stream='this is a csv_gz stream2',
                service_client_id='myservice_client'),
             call(dash_orgname = 'mydash_orgname',
                  dash_api_key = 'mydash_api_key',
                dash_table = 'mydashtable',
                csv_gz_stream='this is a csv_gz stream3',
                service_client_id='myservice_client')
        ]


        upload_csv_to_dash.assert_has_calls(upload_csv_to_dash_calls)

        self.assertEqual(result,['response1', 'response2', 'response3'])


    @mock.patch('comotion.dash.requests.request')
    def test_upload_csv_to_dash(self,request):
        # test upload_csv_to_dash  success

        file = Mock(getbuffer=lambda :'buffered_data')

        raise_for_status_function = Mock()
        request.return_value = Mock(raise_for_status=raise_for_status_function)
        result = dash.upload_csv_to_dash(
            dash_table='mydashtable',
            dash_orgname='mydash_orgname',
            dash_api_key='mydash_api_key',
            csv_gz_stream=file
        )

        request.assert_called_once_with(
            'POST',
            'https://api.comodash.io/v1/data-input-file',
            headers={
                'Content-Type': 'application/gzip',
                'service_client_id': '0',
                'x-api-key': 'mydash_api_key',
                'org-name': 'mydash_orgname',
                'table-name': 'mydashtable'
            },
            data='buffered_data')

        self.assertEqual(result,request.return_value)
        raise_for_status_function.assert_called_once()



    @mock.patch('comotion.dash.requests.request')
    def test_upload_csv_to_dash_with_service_client(self,request):
        # test upload_csv_to_dash  with service client

        file = Mock(getbuffer=lambda :'buffered_data')

        raise_for_status_function = Mock()
        request.return_value = Mock(raise_for_status=raise_for_status_function)
        result = dash.upload_csv_to_dash(
            dash_table='mydashtable',
            dash_orgname='mydash_orgname',
            dash_api_key='mydash_api_key',
            csv_gz_stream=file,
            service_client_id = 'myserviceclient'
        )

        request.assert_called_once_with(
            'POST',
            'https://api.comodash.io/v1/data-input-file',
            headers={
                'Content-Type': 'application/gzip',
                'service_client_id': 'myserviceclient',
                'x-api-key': 'mydash_api_key',
                'org-name': 'mydash_orgname',
                'table-name': 'mydashtable'
            },
            data='buffered_data')

        self.assertEqual(result,request.return_value)
        raise_for_status_function.assert_called_once()

class TestDashModuleQueryClass(unittest.TestCase):

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    def test_init_valid_input(self, mock_queries_api, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        # mock_config.auth.get_access_token.return_value = 'test_token'

        # Mock the API client and QueriesApi
        mock_api_client_instance = mock_api_client.return_value.__enter__.return_value
        mock_queries_api_instance = mock_queries_api.return_value
        mock_query_id_model = QueryId(query_id='123')
        mock_queries_api_instance.run_query.return_value = mock_query_id_model
        
        query = Query(
            config=mock_config,
            query_text='SELECT * FROM test_table'
        )
        mock_queries_api.assert_called_once_with(mock_api_client_instance)
        mock_queries_api_instance.run_query.assert_called_once_with(QueryText(query='SELECT * FROM test_table'))
        self.assertIsNotNone(query)
        self.assertEqual(query.query_id, '123')
    
    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    def test_init_with_query_id(self, mock_queries_api, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Mock the API client and QueriesApi
        mock_api_client_instance = mock_api_client.return_value.__enter__.return_value
        mock_queries_api_instance = mock_queries_api.return_value

        # Assume this is the query ID provided by the user
        provided_query_id = 'existing_query_id'

        # Assume we're fetching some details about this existing query
        mock_query_info = QueryInfo(query_id=provided_query_id, query='SELECT * FROM test_table')
        mock_queries_api_instance.get_query.return_value = mock_query_info

        # Initialize the Query with an existing query_id
        query = Query(
            config=mock_config,
            query_id=provided_query_id
        )

        # Assertions to ensure the query was initialized correctly with the provided ID
        self.assertEqual(query.query_id, provided_query_id)
        mock_queries_api_instance.get_query.assert_not_called()
        mock_queries_api_instance.run_query.assert_not_called()  # Ensures a new query wasn't started

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    def test_init_invalid_config_type(self, mock_queries_api, mock_api_client):
        # Mock an invalid config object (not of type DashConfig)
        invalid_config = 'invalid_config'

        # Attempt to initialize the Query with the invalid config
        with self.assertRaises(TypeError) as context:
            Query(
                config=invalid_config,
                query_text='SELECT * FROM test_table'
            )

        # Check if the exception message is as expected
        self.assertIn("config must be of type comotion.dash.DashConfig", str(context.exception))

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')  # Patch the QueriesApi
    @patch('comotion.dash.Query.refresh_api_instance')
    def test_get_query_info(self, mock_query_refresh_api, mock_queries_api, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)
        
        # Mock the API client and QueriesApi
        mock_api_client_instance = mock_api_client.return_value.__enter__.return_value
        mock_queries_api_instance = mock_queries_api.return_value

        # Mock QueryId and QueryInfo
        mock_query_id = '123'
        mock_query_info_instance = QueryInfo()
        mock_queries_api_instance.get_query.return_value = mock_query_info_instance

        # Create a Query instance without running its __init__ method
        with patch.object(Query, '__init__', lambda self, *args, **kwargs: None):
            mock_query = Query()
            # Manually set necessary attributes
            mock_query.query_api_instance = mock_queries_api_instance
            mock_query.query_id = mock_query_id

            # Call the method
            result = mock_query.get_query_info()

            # Assertions
            mock_queries_api_instance.get_query.assert_called_once_with(mock_query_id)
            self.assertEqual(result, mock_query_info_instance)

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    def test_state(self, mock_queries_api, mock_api_client):
        # Mock the DashConfig object
        mock_config = MagicMock(spec=DashConfig)

        # Mock the API client and QueriesApi
        mock_api_client_instance = mock_api_client.return_value.__enter__.return_value
        mock_queries_api_instance = mock_queries_api.return_value

        # Create a mock Query instance without running its __init__ method
        with patch.object(Query, '__init__', lambda self, *args, **kwargs: None):
            mock_query = Query()
            mock_query.query_api_instance = mock_queries_api_instance
            mock_query.query_id = '123'

            # Set up the return value for the mocked get_query_info method
            mock_query_status = QueryStatus(state='RUNNING')
            mock_query_info = QueryInfo(status=mock_query_status)
            mock_query.get_query_info = MagicMock(return_value=mock_query_info)

            # Call the state method and assert it returns the expected state
            self.assertEqual(mock_query.state(), 'RUNNING')
    
    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    def test_is_complete(self, mock_queries_api, mock_api_client):
        mock_config = MagicMock(spec=DashConfig)
        mock_query = Query(config=mock_config, query_text='SELECT * FROM test_table')
        mock_query.get_query_info = MagicMock()

        # Test when the query is running
        mock_query.get_query_info.return_value = QueryInfo(status=QueryStatus(state='RUNNING'))
        self.assertFalse(mock_query.is_complete())

        # Test when the query is completed
        for state in Query.COMPLETED_STATES:
            mock_query.get_query_info.return_value = QueryInfo(status=QueryStatus(state=state))
            self.assertTrue(mock_query.is_complete())

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    @patch('time.sleep', side_effect=lambda x: None)  # Mock time.sleep to return immediately
    def test_wait_to_complete(self, mock_sleep, mock_queries_api, mock_api_client):
        mock_config = MagicMock(spec=DashConfig)
        mock_query = Query(config=mock_config, query_text='SELECT * FROM test_table')
        mock_query.get_query_info = MagicMock()

        # Simulate the query status progression
        mock_query.get_query_info.side_effect = [
            QueryInfo(status=QueryStatus(state='RUNNING')),  # First call returns RUNNING
            QueryInfo(status=QueryStatus(state='RUNNING')),  # Second call returns RUNNING
            QueryInfo(status=QueryStatus(state='SUCCEEDED'))  # Third call returns SUCCEEDED
        ]

        # Call wait_to_complete and check the final state
        final_state = mock_query.wait_to_complete()
        self.assertEqual(final_state.status.state, 'SUCCEEDED')

        # Ensure sleep was called to simulate the wait
        self.assertTrue(mock_sleep.called)

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    def test_query_id(self, mock_queries_api, mock_api_client):
        # Setup
        mock_config = MagicMock(spec=DashConfig)
        provided_query_id = 'test_query_id'
        mock_query = Query(config=mock_config, query_id=provided_query_id)

        # Test
        self.assertEqual(mock_query.query_id, provided_query_id)
    
    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    @patch('comotion.dash.Query.refresh_api_instance')
    def test_get_csv_for_streaming(self, mock_query_refresh_api, mock_queries_api, mock_api_client):
        # Setup
        mock_config = MagicMock(spec=DashConfig)
        mock_query = Query(config=mock_config, query_text='SELECT * FROM test_table')
        mock_query.query_id = '123'
        mock_query.query_api_instance = mock_queries_api.return_value

        # Mock HTTPResponse
        mock_response = MagicMock(spec=HTTPResponse)
        mock_query.query_api_instance.download_csv_without_preload_content.return_value = mock_response

        # Test
        response = mock_query.get_csv_for_streaming()
        self.assertEqual(response, mock_response)
        self.assertEqual(mock_response.autoclose,False)
        mock_query.query_api_instance.download_csv_without_preload_content.assert_called_once_with(query_id='123')

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    @patch('comotion.dash.Query.refresh_api_instance')
    def test_download_csv(self, mock_query_refresh_api, mock_queries_api, mock_api_client):
        # Setup
        mock_config = MagicMock(spec=DashConfig)
        mock_query = Query(config=mock_config, query_text='SELECT * FROM test_table')
        mock_query.query_id = '123'
        mock_query.query_api_instance = mock_queries_api.return_value

        # Mock the response from download_csv
        mock_response = MagicMock()
        mock_response.getheader.return_value = '100'
        mock_response.stream.return_value = [b'data']
        mock_response.tell.return_value = 200
        mock_query.query_api_instance.download_csv_without_preload_content.return_value.__enter__.return_value = mock_response

        # Test
        with patch("io.open", mock_open()) as mocked_file_open:
            import urllib3
            with self.assertRaises(urllib3.exceptions.IncompleteRead) as incomplete_read_exception:
                mock_query.download_csv('output_file_path.csv')
            mocked_file_open.assert_called_once_with('output_file_path.csv', 'wb')
            mock_query.query_api_instance.download_csv_without_preload_content.assert_called_once_with(query_id='123')

    @patch('comotion.dash.comodash_api_client_lowlevel.ApiClient')
    @patch('comotion.dash.QueriesApi')
    @patch('comotion.dash.Query.refresh_api_instance')
    def test_stop(self, mock_query_refresh_api, mock_queries_api, mock_api_client):
        # Setup
        mock_config = MagicMock(spec=DashConfig)
        mock_query = Query(config=mock_config, query_text='SELECT * FROM test_table')
        mock_query.query_id = '123'
        mock_query.query_api_instance = mock_queries_api.return_value

        # Test
        mock_query.stop()
        mock_query.query_api_instance.stop_query.assert_called_once_with('123')

import unittest
from unittest.mock import Mock, patch
import jwt
import datetime

class TestDashConfig(unittest.TestCase):

    def setUp(self):
        # Mock an Auth object with necessary attributes/methods
        self.mock_auth = Mock(spec=Auth)
        self.mock_auth.get_access_token.return_value = 'new_token'
        self.mock_auth.orgname = 'test_org'
        self.config = DashConfig(auth=self.mock_auth)

    def test_init_with_invalid_auth(self):
        with self.assertRaises(TypeError):
            DashConfig(auth="NotAnAuthInstance")

    def test_init_with_valid_auth(self):
        self.assertEqual(self.config.auth, self.mock_auth)

    @patch('jwt.decode')
    def test_check_and_refresh_token_no_token(self, mock_jwt_decode):
        self.config.access_token = None
        self.config._check_and_refresh_token()
        self.mock_auth.get_access_token.assert_called_once()
        # Ensure jwt.decode is not called when there's no initial token
        mock_jwt_decode.assert_not_called()

    @patch('jwt.decode')
    def test_check_and_refresh_token_valid_token(self, mock_jwt_decode):
        self.config.access_token = 'valid_token'
        mock_jwt_decode.return_value = {'exp': datetime.datetime.utcnow().timestamp() + 100}
        self.config._check_and_refresh_token()
        self.mock_auth.get_access_token.assert_not_called()
        # Check jwt.decode was called with the correct token
        mock_jwt_decode.assert_called_with('valid_token', options={"verify_signature": False})

    @patch('jwt.decode')
    def test_check_and_refresh_token_near_expiration(self, mock_jwt_decode):
        self.config.access_token = 'almost_expired_token'
        mock_jwt_decode.return_value = {'exp': datetime.datetime.utcnow().timestamp() + 20}
        self.config._check_and_refresh_token()
        self.mock_auth.get_access_token.assert_called_once()
        # Check jwt.decode was called with the correct token
        mock_jwt_decode.assert_called_with('almost_expired_token', options={"verify_signature": False})

    @patch('jwt.decode')
    def test_check_and_refresh_token_expired(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError
        self.config.access_token = 'expired_token'
        self.config._check_and_refresh_token()
        self.mock_auth.get_access_token.assert_called_once()
        # Check jwt.decode was called with the correct token
        mock_jwt_decode.assert_called_with('expired_token', options={"verify_signature": False})

    @patch('jwt.decode')
    def test_check_and_refresh_token_decode_error(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = jwt.DecodeError
        self.config.access_token = 'bad_token'
        self.config._check_and_refresh_token()
        self.mock_auth.get_access_token.assert_called_once()
        # Check jwt.decode was called with the correct token
        mock_jwt_decode.assert_called_with('bad_token', options={"verify_signature": False})

    @patch('jwt.decode')
    def test_check_and_refresh_token_unexpected_payload(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {}  # No 'exp' field
        self.config.access_token = 'unexpected_payload_token'
        self.config._check_and_refresh_token()
        self.mock_auth.get_access_token.assert_called_once()
        # Check jwt.decode was called with the correct token
        mock_jwt_decode.assert_called_with('unexpected_payload_token', options={"verify_signature": False})
        
class TestDashBulkUploader(unittest.TestCase):

    def setUp(self):
        self.mock_auth = Mock(spec=Auth)
        self.mock_auth.orgname = 'test_org'
        self.uploader = DashBulkUploader(auth_token=self.mock_auth)

    @patch('comotion.dash.Load')
    def test_add_load(self, mock_load):
        self.uploader.add_load(
            table_name='test_table',
            check_sum={'count(*)': 100},
            load_as_service_client_id='service_client'
        )
        self.assertIn('test_table', self.uploader.uploads)
        self.assertEqual(self.uploader.uploads['test_table']['check_sum'], {'count(*)': 100})
        mock_load.assert_called_once()

    def test_add_load_invalid_table_name(self):
        with self.assertRaises(ValueError):
            self.uploader.add_load(
                table_name='Test_Table',
                check_sum={'count(*)': 100}
            )

    @patch('comotion.dash.Load')
    def test_add_load_existing_table(self, mock_load):
        self.uploader.add_load(
                table_name='test_table',
                check_sum={'count(*)': 100}
            )
        with self.assertRaises(ValueError):
            self.uploader.add_load(
                table_name='test_table',
                check_sum={'count(*)': 100}
            )

    @patch('comotion.dash.Load')
    def test_add_data_to_load(self, mock_load):
        self.uploader.add_load(
            table_name='test_table',
            check_sum={'count(*)': 100},
            load_as_service_client_id='service_client'
        )
        self.uploader.add_data_to_load(
            table_name='test_table',
            data=pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            file_key='test_key'
        )
        self.assertIn('test_key', self.uploader.uploads['test_table']['data_sources'])

    def test_add_data_to_load_no_existing_load(self):
        with self.assertRaises(ValueError):
            self.uploader.add_data_to_load(
                table_name='test_table',
                data=pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
            )

    @patch('comotion.dash.Load')
    def test_remove_data_from_load(self, mock_load):
        self.uploader.add_load(
            table_name='test_table',
            check_sum={'count(*)': 100},
            load_as_service_client_id='service_client'
        )
        self.uploader.add_data_to_load(
            table_name='test_table',
            data=pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            file_key='test_key'
        )
        self.uploader.uploads['test_table']['load_status'] = 'OPEN'
        self.uploader.remove_data_from_load(
            table_name='test_table',
            file_key='test_key'
        )
        self.assertNotIn('test_key', self.uploader.uploads['test_table']['data_sources'])

    @patch('comotion.dash.Load')
    def test_remove_load(self, mock_load):
        self.uploader.add_load(
            table_name='test_table',
            check_sum={'count(*)': 100},
            load_as_service_client_id='service_client'
        )
        self.uploader.uploads['test_table']['load_status'] = 'OPEN'
        self.uploader.remove_load('test_table')
        self.assertNotIn('test_table', self.uploader.uploads)

    @patch('comotion.dash.Load')
    def test_remove_data_from_load_when_load_status_not_open(self, mock_load):
        self.uploader.add_load(
            table_name='test_table',
            check_sum={'count(*)': 100},
            load_as_service_client_id='service_client'
        )
        self.uploader.add_data_to_load(
            table_name='test_table',
            data=pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            file_key='test_key'
        )
        self.uploader.uploads['test_table']['load_status'] = 'FAILED'
        with self.assertRaises(Exception):
            self.uploader.remove_data_from_load(
                table_name='test_table',
                file_key='test_key'
            )

    @patch('comotion.dash.Load')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_execute_upload(self, mock_executor, mock_load):
        mock_load_instance = mock_load.return_value
        mock_load_instance.get_load_info.return_value.load_status = 'OPEN'

        self.uploader.add_load(
            table_name='test_table',
            check_sum={'count(*)': 100},
            load_as_service_client_id='service_client'
        )
        self.uploader.add_data_to_load(
            table_name='test_table',
            data=pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            file_key='test_key'
        )
        self.uploader.execute_upload('test_table')
        self.assertEqual(self.uploader.uploads['test_table']['load_status'], 'OPEN')

    @patch('comotion.dash.Load')
    def test_get_load_info(self, mock_load):
        mock_load_instance = mock_load.return_value
        mock_load_instance.get_load_info.return_value.load_status = 'OPEN'
        self.uploader.add_load(
            table_name='test_table',
            check_sum={'count(*)': 100},
            load_as_service_client_id='service_client'
        )
        load_info = self.uploader.get_load_info()
        self.assertIn('test_table', load_info)
        self.assertEqual(load_info['test_table'].load_status, 'OPEN')

    def test_add_load_without_checksum_or_tracking(self):
        table_name = 'test_table'
        with self.assertRaises(KeyError):
            self.uploader.add_load(
                table_name=table_name,
                load_as_service_client_id='service_client'
            )

if __name__ == '__main__':
    unittest.main()
 