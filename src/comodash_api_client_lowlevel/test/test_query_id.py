# coding: utf-8

"""
    Comotion Dash API

    Comotion Dash API

    The version of the OpenAPI document: 2.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from comodash_api_client_lowlevel.models.query_id import QueryId

class TestQueryId(unittest.TestCase):
    """QueryId unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> QueryId:
        """Test QueryId
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `QueryId`
        """
        model = QueryId()
        if include_optional:
            return QueryId(
                query_id = 's06ba1d95-8c4f-460c-90b3-bc68fddf2fde'
            )
        else:
            return QueryId(
                query_id = 's06ba1d95-8c4f-460c-90b3-bc68fddf2fde',
        )
        """

    def testQueryId(self):
        """Test QueryId"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
