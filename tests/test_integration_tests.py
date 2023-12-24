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
from keyrings.cryptfile.file import PlaintextKeyring
#this is a module that acts as the local keyring so this test can be run in locations without

class TestIntegrationTests(unittest.TestCase):



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
        validation_error = None
        result =None
        try:
            runner = CliRunner()
            result = runner.invoke(
                cli=cli.cli,
                args=cli_args,
                env={"COMOTION_ORGNAME": "test1"},
                catch_exceptions=False
            )
        except pydantic_core._pydantic_core.ValidationError as ve:
            validation_error = ve

        # Assertions to ensure the command was called correctly
        if result is not None:
            print(result.output)
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
        self.assertEquals(mock_urllib3_request.mock_calls, mock_calls)
        mock_urllib3_request.assert_has_calls(mock_calls, any_order=False)
        self.assertEqual(mock_urllib3_request.call_count, len(expected_calls))

        # assert that auth call happened properly
        mock_requests_post.assert_called_once_with('https://auth.comotion.us/auth/realms/test1/protocol/openid-connect/token', data={'grant_type': 'refresh_token', 'refresh_token': 'myrefreshtoken', 'client_id': 'comotion_cli'})

        # delaying this assertion allows us to see the actual calls while developnig the tests
        if validation_error is not None:
            raise validation_error

        # Check the output
        self.assertEquals(expected_result, result.output)



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
    def test_dash_download_csv(self, mock_requests_post, mock_urllib3_request):
        # with mock.patch('io.open',  new_callable=mock.mock_open) as mock_io_open:
            self._generic_integration_test(
                mock_requests_post=mock_requests_post,
                mock_urllib3_request=mock_urllib3_request,
                cli_args=['dash','download','-f ./integration_tests_out.csv','--query_id','myqueryid'],
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
                            data=b'{"queryId": "12345", "status": {"state": "FAILED", "state_change_reason":"THIS IS A BAD REASON"}}'
                        )
                    }
                ],
                expected_result='FAILED - THIS IS A BAD REASON\n'
            )

            # Verify the file was opened in write-binary mode and the correct content was written
            # mock_io_open.assert_called_once_with('output.csv', 'wb')  # Adjust if your function uses different parameters
            # mock_io_open().write.assert_called_once_with(b'some,csv,data\n1,2,3\n')
            # mock_io_open.stop()

    # urllib3.PoolManager.request is used by the lowlevel api to make calls
    # requests class is used by Auth class
    # @mock.patch('urllib3.PoolManager.request')
    # @mock.patch('requests.post')
    # def test_dash_stop_query_generic(self, mock_requests_post, mock_urllib3_request):
    #     self._generic_integration_test(
    #         mock_requests_post=mock_requests_post,
    #         mock_urllib3_request=mock_urllib3_request,
    #         expected_http_call_type='DELETE',
    #         cli_args=['dash','stop-query','--query_id','myqueryid'],
    #         expected_http_call_url='https://test1.api.comodash.io/v2/query/12345',
    #         expected_http_call_body='',
    #         expected_result='12345'
    #     )


if __name__ == '__main__':
    unittest.main()
