# this file contains integration tests that test integration of cli, sdk and low_level sdk
# it does this by calling cli functions, but then mocking and testing the urllib3 requests made by the low level sdk.
# this ensures that the actual calls made by the framework are correct

import unittest
import comotion
from unittest import mock
from click.testing import CliRunner
from comotion import cli  
import os
import pydantic_core
import json
from keyrings.cryptfile.file import PlaintextKeyring
#this is a module that acts as the local keyring so this test can be run in locations without
import awswrangler as wr


class TestIntegrationTests(unittest.TestCase):

    ## Set the maximum size of the assertion error message when Unit Test fail
    maxDiff = None

    def _generic_integration_test(
            self, 
            mock_requests_post, 
            mock_urllib3_request, 
            cli_args,
            expected_result,
            expected_calls = []):
        """
        Utility function that runs integration tests for cli > sdk > lowlevel sdk
        It mocks the lowest level call (urllib3 and requests) so it tests all the layers together/


            urllib3.PoolManager.request is used by the lowlevel api to make calls
            `requests` class is used by Auth class
        """
        os.environ['KEYRING_CRYPTFILE_PASSWORD']='mypassword'
        kr = PlaintextKeyring()
        kr.set_password('comotion auth api latest username (https://auth.comotion.us)','test1','myusername')
        kr.set_password("comotion auth api offline token (https://auth.comotion.us/auth/realms/test1)",'myusername','myrefreshtoken')

        #setup requests mock to return an access token of sorts
        requests_response = mock.MagicMock()
        requests_response.status_code = 200
        requests_response.text='{"access_token": "myaccesstoken"}'
        mock_requests_post.return_value = requests_response

        # Setup the mock to return a fake response
        side_effects = []
        for expected_call in expected_calls:
            mock_urllib3_response = expected_call['response']
            side_effects.append(mock_urllib3_response)
        if len(side_effects) == 1:
            mock_urllib3_request.return_value = side_effects[0]
        else:
            mock_urllib3_request.side_effect = side_effects
        
        
        # Setup the CliRunner to invoke your CLI command
        print("invoke cli runner")
        validation_error = None
        result =None
        try:
            runner = CliRunner()
            # with runner.isolated_filesystem(temp_dir=None):
            result = runner.invoke(
                cli=cli.cli,
                args=cli_args,
                env={"COMOTION_ORGNAME": "test1"},
                catch_exceptions=False
            )
        except pydantic_core._pydantic_core.ValidationError as ve:
            print("validation error caputed. will be rethrown after other asserts")
            validation_error = ve

        # Assertions to ensure the command was called correctly
        if result is not None:
            print("START"+result.output+"END")
            print(result.exception)
            print(result.exc_info)
            self.assertEqual(result.exit_code, 0)


        # assert that api call happened properly
        mock_calls=[]
        for expected_call in expected_calls:
            # mock_urllib3_request.assert_called_once_with(
            mock_call=expected_call['request']
            mock_calls.append(mock_call)
        print(mock_urllib3_request.mock_calls)
        self.assertEqual(mock_urllib3_request.mock_calls, mock_calls)
        mock_urllib3_request.assert_has_calls(mock_calls, any_order=False)
        self.assertEqual(mock_urllib3_request.call_count, len(expected_calls))

        # assert that auth call happened properly
        mock_requests_post.assert_called_once_with('https://auth.comotion.us/auth/realms/test1/protocol/openid-connect/token', data={'grant_type': 'refresh_token', 'refresh_token': 'myrefreshtoken', 'client_id': 'comotion_cli'})

        # delaying this assertion allows us to see the actual calls while developnig the tests
        if validation_error is not None:
            raise validation_error

        # Check the output
        self.assertEqual(expected_result, result.output)



    ###############################################################################################
    ############################  QUERY CLI TEST ##################################################
    ###############################################################################################
        

    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    def test_dash_start_query_generic(self, mock_requests_post, mock_urllib3_request):
        self._generic_integration_test(
            mock_requests_post=mock_requests_post,
            mock_urllib3_request=mock_urllib3_request,
            cli_args=['dash','start-query','SELECT * FROM table'],
            expected_calls=[
                {   # start query call
                    'request': unittest.mock.call(
                        'POST', 
                        'https://test1.api.comodash.io/v2/query', 
                        body='{"query": "SELECT * FROM table"}', 
                        timeout=None, 
                        headers={
                            'Accept': 'application/json', 
                            'Content-Type': 'application/json', 
                            'User-Agent': 'OpenAPI-Generator/1.0.0/python', 
                            'Authorization': 'Bearer myaccesstoken'
                        }, 
                        preload_content=False
                    ),                    
                    'response': mock.MagicMock(
                        headers={'header1': "2"}, 
                        status=202, 
                        data=b'{"queryId": "12345"}'
                    )
                },
            ],
            expected_result='12345\n'
        )

    # urllib3.PoolManager.request is used by the lowlevel api to make calls
    # requests class is used by Auth class
    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    def test_dash_stop_query(self, mock_requests_post, mock_urllib3_request):
        self._generic_integration_test(
            mock_requests_post=mock_requests_post,
            mock_urllib3_request=mock_urllib3_request,
            cli_args=['dash','stop-query','--query_id','myqueryid'],
            expected_calls=[
                # {  # get query info run when Query object is initialised
                #     'request': unittest.mock.call(
                #         'GET', 
                #         'https://test1.api.comodash.io/v2/query/myqueryid', 
                #         fields={},
                #         timeout=None, 
                #         headers={
                #             'Accept': 'application/json',
                #             'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                #             'Authorization': 'Bearer myaccesstoken'
                #         }, 
                #         preload_content=False),
                #     'response': mock.MagicMock(
                #         headers={'header1': "2"}, 
                #         status=200, 
                #         data=b'{"queryId": "12345"}'
                #     )
                # },
                {   # delete request
                    'request': unittest.mock.call(
                        'DELETE',
                        'https://test1.api.comodash.io/v2/query/myqueryid',
                        body=None,
                        timeout=None,
                        headers={
                                'Accept': 'application/json',
                                'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                                'Authorization': 'Bearer myaccesstoken'
                        }, 
                        preload_content=False
                    ),
                    'response': mock.MagicMock(
                        headers={'header1': "2"}, 
                        status=202, 
                        data=b''
                    )
                }
                
            ],
            expected_result='Query stopped\n'
        )

    # urllib3.PoolManager.request is used by the lowlevel api to make calls
    # requests class is used by Auth class
    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    def test_dash_get_query_state(self, mock_requests_post, mock_urllib3_request):
        self._generic_integration_test(
            mock_requests_post=mock_requests_post,
            mock_urllib3_request=mock_urllib3_request,
            cli_args=['dash','query-info','--query_id','myqueryid'],
            expected_calls=[
                {  # get query info run when Query object is initialised
                    'request': unittest.mock.call(
                        'GET', 
                        'https://test1.api.comodash.io/v2/query/myqueryid', 
                        fields={},
                        timeout=None, 
                        headers={
                            'Accept': 'application/json',
                            'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                            'Authorization': 'Bearer myaccesstoken'
                        }, 
                        preload_content=False),
                    'response': mock.MagicMock(
                        headers={'header1': "2"}, 
                        status=200, 
                        data=b'{"queryId": "12345", "status": {"state": "RUNNING"}}'
                    )
                }
            ],
            expected_result='RUNNING\n'
        )


    # urllib3.PoolManager.request is used by the lowlevel api to make calls
    # requests class is used by Auth class
    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    def test_dash_get_query_state_error(self, mock_requests_post, mock_urllib3_request):
        self._generic_integration_test(
            mock_requests_post=mock_requests_post,
            mock_urllib3_request=mock_urllib3_request,
            cli_args=['dash','query-info','--query_id','myqueryid'],
            expected_calls=[
                {  # get query info run when Query object is initialised
                    'request': unittest.mock.call(
                        'GET', 
                        'https://test1.api.comodash.io/v2/query/myqueryid', 
                        fields={},
                        timeout=None, 
                        headers={
                            'Accept': 'application/json',
                            'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                            'Authorization': 'Bearer myaccesstoken'
                        }, 
                        preload_content=False),
                    'response': mock.MagicMock(
                        headers={'header1': "2"}, 
                        status=200, 
                        data=b'{"queryId": "12345", "status": {"state": "FAILED", "stateChangeReason":"THIS IS A BAD REASON"}}'
                    )
                }
            ],
            expected_result='FAILED - THIS IS A BAD REASON\n'
        )

    # urllib3.PoolManager.request is used by the lowlevel api to make calls
    # requests class is used by Auth class
    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    def test_dash_download_csv_success(self, mock_requests_post, mock_urllib3_request):
        # with mock.patch('io.open',  new_callable=mock.mock_open) as mock_io_open:
            download_response = mock.MagicMock(
                            headers={'header1': "2"}, 
                            status=200, 
                            data=b'this is a bytestream'
                        )
            download_response.__enter__.return_value.tell.return_value = 54321
            #this is used in the guts of the download to get the content-header
            download_response.__enter__.return_value.getheader.return_value = "54321"
            data_stream_list = []
            data_stream_list.append(b'this is a bytestream1')
            data_stream_list.append(b'this is a bytestream2')
            data_stream_list.append(b'this is a bytestream3')
            data_stream_list.append(b'this is a bytestream4')
            data_stream_list.append(b'this is a bytestream5')
            data_stream_list.append(b'this is a bytestream6')
            data_stream_list.append(b'this is a bytestream7')
            download_response.__enter__.return_value.stream.return_value=iter(data_stream_list)
            self._generic_integration_test(
                mock_requests_post=mock_requests_post,
                mock_urllib3_request=mock_urllib3_request,
                cli_args=['dash','download','-fintegration_tests_out.csv','my select statement'],
                expected_calls=[
                    {  # get query info run when Query object is initialised and in running state
                        'request': unittest.mock.call(
                            'POST', 
                            'https://test1.api.comodash.io/v2/query', 
                            body='{"query": "my select statement"}',
                            timeout=None, 
                            headers={
                                'Accept': 'application/json',
                                 'Content-Type': 'application/json',
                                'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                                'Authorization': 'Bearer myaccesstoken'
                            }, 
                            preload_content=False),
                        'response': mock.MagicMock(
                            headers={'header1': "2"}, 
                            status=202, 
                            data=b'{"queryId": "12345"}'
                        )
                    },
                    {  # get query info run when Query object is initialised and in running state
                        'request': unittest.mock.call(
                            'GET', 
                            'https://test1.api.comodash.io/v2/query/12345', 
                            fields={},
                            timeout=None, 
                            headers={
                                'Accept': 'application/json',
                                'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                                'Authorization': 'Bearer myaccesstoken'
                            }, 
                            preload_content=False),
                        'response': mock.MagicMock(
                            headers={'header1': "2"}, 
                            status=200, 
                            data=b'{"queryId": "12345", "query": "select soemthing that that thing",  "status": {"state": "RUNNING", "stateChangeReason": "my reason", "submissionDateTime": "my date", "completion_date_time": "my other date"}, "statementType": "ITranscendTypes1"}'
                        )
                    },
                    {  # get query info run when Query object is initialised and in running state
                        'request': unittest.mock.call(
                            'GET', 
                            'https://test1.api.comodash.io/v2/query/12345', 
                            fields={},
                            timeout=None, 
                            headers={
                                'Accept': 'application/json',
                                'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                                'Authorization': 'Bearer myaccesstoken'
                            }, 
                            preload_content=False),
                        'response': mock.MagicMock(
                            headers={'header1': "2"}, 
                            status=200, 
                            data=b'{"queryId": "12345", "query": "select soemthing that that thing",  "status": {"state": "RUNNING", "stateChangeReason": "my reason", "submissionDateTime": "my date", "completion_date_time": "my other date"}, "statementType": "ITranscendTypes1"}'
                        )
                    },
                    {  # get query info run when Query object is initialised and in SUCCESS state
                        'request': unittest.mock.call(
                            'GET', 
                            'https://test1.api.comodash.io/v2/query/12345', 
                            fields={},
                            timeout=None, 
                            headers={
                                'Accept': 'application/json',
                                'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                                'Authorization': 'Bearer myaccesstoken'
                            }, 
                            preload_content=False),
                        'response': mock.MagicMock(
                            headers={'header1': "2"}, 
                            status=200, 
                            data=b'{"queryId": "12345", "status": {"state": "SUCCEEDED"}}'
                        )
                    },
                    {  # get query info run when Query object is initialised and in SUCCESS state
                        'request': unittest.mock.call(
                            'GET', 
                            'https://test1.api.comodash.io/v2/query/12345/csv', 
                            fields={},
                            timeout=None, 
                            headers={
                                'Accept': 'application/json',
                                'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                                'Authorization': 'Bearer myaccesstoken'
                            }, 
                            preload_content=False),
                        'response': download_response
                    }
                ],
                expected_result="""running query...
query initiated
query complete
Downloading to integration_tests_out.csv
finalising file...
"""
            )

            import os
            print("Current Working Directory:", os.getcwd())

            # Reading the content of the file and assert it is correct
            file_path = os.getcwd()+'/integration_tests_out.csv'
            with open(file_path, 'r') as file:
                content = file.read()
            self.assertEqual(content,'this is a bytestream1this is a bytestream2this is a bytestream3this is a bytestream4this is a bytestream5this is a bytestream6this is a bytestream7')
            try:
                os.remove(file_path)
                print(f"File {file_path} has been deleted successfully")
            except FileNotFoundError:
                print(f"The file {file_path} does not exist")

    ###############################################################################################
    ############################  LOAD CLI TESTS  #################################################
    ###############################################################################################


    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    def test_dash_create_load(self, mock_requests_post, mock_urllib3_request):
        # Define the CLI arguments for creating a load
        cli_args = ['dash', 'create-load', '--load-type', 'APPEND_ONLY', 'my_table_name']

        # Define the expected calls to the lower-level SDK/API
        expected_calls = [
            {
                'request': unittest.mock.call(
                    'POST',
                    'https://test1.api.comodash.io/v2/load',
                    body=json.dumps({"load_type": "APPEND_ONLY", "table_name": "my_table_name", "partitions": []}),
                    timeout=None,
                    headers={
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                        'Authorization': 'Bearer myaccesstoken'
                    },
                    preload_content=False
                ),
                'response': mock.MagicMock(
                    headers={'header1': "2"},
                    status=202,
                    data=b'{"loadId": "load12345"}'
                )
            }
        ]

        # Define the expected result/output from the CLI command
        expected_result = 'load12345\n'

        # Call the generic integration test function with the above parameters
        self._generic_integration_test(
            mock_requests_post=mock_requests_post,
            mock_urllib3_request=mock_urllib3_request,
            cli_args=cli_args,
            expected_calls=expected_calls,
            expected_result=expected_result
        )
    
    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    def test_dash_create_load_with_partitions_and_service_client_id(self, mock_requests_post, mock_urllib3_request):
        # Define the CLI arguments for creating a load
        cli_args = ['dash', 'create-load', '--load-type', 'APPEND_ONLY', '--load-as-service-client', 'myserviceclient','-pabc','-pdef', 'my_table_name']

        # Define the expected calls to the lower-level SDK/API
        expected_calls = [
            {
                'request': unittest.mock.call(
                    'POST',
                    'https://test1.api.comodash.io/v2/load',
                    body=json.dumps({"load_type": "APPEND_ONLY", "table_name": "my_table_name", "load_as_service_client_id": 'myserviceclient', "partitions": ['abc','def'], }),
                    timeout=None,
                    headers={
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                        'Authorization': 'Bearer myaccesstoken'
                    },
                    preload_content=False
                ),
                'response': mock.MagicMock(
                    headers={'header1': "2"},
                    status=202,
                    data=b'{"loadId": "load12345"}'
                )
            }
        ]

        # Define the expected result/output from the CLI command
        expected_result = 'load12345\n'

        # Call the generic integration test function with the above parameters
        self._generic_integration_test(
            mock_requests_post=mock_requests_post,
            mock_urllib3_request=mock_urllib3_request,
            cli_args=cli_args,
            expected_calls=expected_calls,
            expected_result=expected_result
        )

    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    @mock.patch('boto3.Session')
    @mock.patch('awswrangler.s3.upload')
    @mock.patch('click.open_file')
    def test_dash_upload_file(self, click_open_file, wr_s3_upload, boto3_session, mock_requests_post, mock_urllib3_request):
        # Define the CLI arguments for uploading a file to a load
        cli_args = ['dash', 'upload-file', '--load_id', 'load12345', '--file_key', 'unique_file_key', 'input_file.parquet']

        boto3_session.return_value = mock.MagicMock()
        session_object = boto3_session.return_value
        click_file_opened  = click_open_file.return_value.__enter__.return_value

        ## Create file
        import pandas as pd
        import pyarrow.parquet as pq

        # Create a simple DataFrame
        df = pd.DataFrame({
            'Column1': [1, 2, 3],
            'Column2': ['A', 'B', 'C']
        })

        # Define the path for the dummy parquet file
        file_path = 'input_file.parquet'

        # Convert the DataFrame to a Parquet file
        df.to_parquet(file_path)

        # Define the expected calls to the lower-level SDK/API
        expected_calls = [
            {
                'request': unittest.mock.call(
                    'POST',
                    'https://test1.api.comodash.io/v2/load/load12345/file',
                    body='{"file_key": "unique_file_key"}',  # This should be the binary content of the file or a reference to the file.
                    timeout=None,
                    headers={
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                        'Authorization': 'Bearer myaccesstoken'
                    },
                    preload_content=False
                ),
                'response': mock.MagicMock(
                    headers={'header1': "2"},
                    status=200,
                    data=b'{"presigned_url": "my presigned url", "sts_credentials": {"AccessKeyId": "myaccesskey", "SecretAccessKey": "mysecret", "SessionToken": "mysession"}, "bucket": "mybucket", "path": "mypath"}'
                )
            }
        ]

        # Define the expected result/output from the CLI command
        expected_result = 'getting upload info\nuploading file\n'

        # Call the generic integration test function with the above parameters
        self._generic_integration_test(
            mock_requests_post=mock_requests_post,
            mock_urllib3_request=mock_urllib3_request,
            cli_args=cli_args,
            expected_calls=expected_calls,
            expected_result=expected_result
        )
        print(click_open_file.mock_calls)
        # check that boto3 session is created properly
        self.assertEqual(
            [unittest.mock.call(aws_access_key_id='myaccesskey', aws_secret_access_key='mysecret', aws_session_token='mysession')],
            boto3_session.mock_calls
        )
        # check that the aws wrangler is called in the right way.
        # decided not to mock the underlying calls of aws wrangler because that is subject to change
        self.assertEqual(
            [unittest.mock.call(local_file=click_file_opened, path='s3://mybucket/mypath', boto3_session=session_object, use_threads=True)],
            wr_s3_upload.mock_calls
        )

        # check that the local file is called correctly

        self.assertEqual(
            unittest.mock.call('/Users/timothyvieyra/Documents/comotion-sdk/input_file.parquet', 'rb'),
            click_open_file.mock_calls[0]
        )

if __name__ == '__main__':
    unittest.main()
