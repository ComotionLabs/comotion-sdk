# this file contains integration tests that test integration of cli, sdk and low_level sdk
# it does this by calling cli functions, but then mocking and testing the urllib3 requests made by the low level sdk.
# this ensures that the actual calls made by the framework are correct

import unittest
from unittest import mock
from click.testing import CliRunner
from comotion import cli  
class TestDashStartQueryCommand(unittest.TestCase):
    # urllib3.PoolManager.request is used by the lowlevel api to make calls
    # requests class is used by Auth class
    @mock.patch('urllib3.PoolManager.request')
    @mock.patch('requests.post')
    def test_dash_start_query(self, mock_requests_post, mock_urllib3_request):
        # Setup the mock to return a fake response
        mock_urllib3_response = mock.MagicMock(headers={'header1': "2"}, status=202, data=b'{"queryId": "12345"}')
        mock_urllib3_request.return_value = mock_urllib3_response

        #setup requests mock to return an access token of sorts
        requests_response = mock.MagicMock()
        requests_response.status_code = 200
        requests_response.text='{"access_token": "myaccesstoken"}'
        mock_requests_post.return_value = requests_response

        # Setup the CliRunner to invoke your CLI command
        runner = CliRunner()
        result = runner.invoke(
            cli=cli.cli,
            args=['dash','start-query','SELECT * FROM table'],
            env={"COMOTION_ORGNAME": "test1"}
        )

        # Assertions to ensure the command was called correctly
        self.assertEqual(result.exit_code, 0)
        mock_urllib3_request.assert_called_once_with(
            'POST',
            'https://test1.api.comodash.io/v2/query',  # Replace with the actual URL path your CLI hits
            body='{"query": "SELECT * FROM table"}',
            timeout=None,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'OpenAPI-Generator/1.0.0/python',
                'Authorization': 'Bearer myaccesstoken'
            },
            preload_content=False
        )
        # Check the output
        self.assertIn('12345', result.output)

if __name__ == '__main__':
    unittest.main()
