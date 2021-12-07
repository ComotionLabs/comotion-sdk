from unittest.mock import patch, Mock
import unittest
from comotion import Auth

from comotion.dash import DashConfig

class MyTestCase(unittest.TestCase):
    def testInitFailValidation(self):

        dash_config = Mock(DashConfig)


        Dash(config=dash_config)
        # does not throw error
        assert True
