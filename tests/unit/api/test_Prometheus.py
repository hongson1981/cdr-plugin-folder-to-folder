from os import environ
from unittest import TestCase
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

import requests
from prometheus_client import start_http_server

class test_Prometheus(TestCase):

    def setUp(self) -> None:
        pass

    def test_prometheus_data(self):
        prometheus_port = 8000
        start_http_server(prometheus_port)
        prometheus_url = f'http://localhost:{prometheus_port}'
        prometheus_data = requests.get(prometheus_url).text
        assert prometheus_data
