import unittest
from unittest import mock
from unittest.mock import Mock
from unittest.mock import call
from comotion import dash
import requests
import io

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
            encoding='utf-8')


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
            encoding='utf-8')


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

if __name__ == '__main__':
    unittest.main()
