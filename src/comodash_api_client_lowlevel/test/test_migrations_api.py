# coding: utf-8

"""
    Comotion Dash API

    Comotion Dash API

    The version of the OpenAPI document: 2.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from comodash_api_client_lowlevel.api.migrations_api import MigrationsApi


class TestMigrationsApi(unittest.TestCase):
    """MigrationsApi unit test stubs"""

    def setUp(self) -> None:
        self.api = MigrationsApi()

    def tearDown(self) -> None:
        pass

    def test_start_migration(self) -> None:
        """Test case for start_migration

        Run migration from Lake V1 to Lake V2
        """
        pass


if __name__ == '__main__':
    unittest.main()