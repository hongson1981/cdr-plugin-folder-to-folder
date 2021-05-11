import asyncio
from unittest import TestCase
from unittest.mock import patch

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import file_contents_as_bytes, folder_exists
from osbot_utils.utils.Json import str_to_json, json_to_str, json_parse

#from cdr_plugin_folder_to_folder.utils.Logging import log_info, log_debug
#from cdr_plugin_folder_to_folder.utils.Logging_Process import start_logging
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
from cdr_plugin_folder_to_folder.utils.testing.Temp_Config import Temp_Config
from cdr_plugin_folder_to_folder.processing.Endpoint_Service import Endpoint_Service

from unittest.mock import create_autospec, MagicMock

class test_Endpoint_Service(Temp_Config):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self) -> None:
        Setup_Testing()
        self.endpoint_service = Endpoint_Service()
        self.mock_ips = '{"live_ips":[10.1.1.10, 10.1.1.11, 10.1.11.12]}'

    def test_get_endpoints(self):
        self.endpoint_service.reset()
        assert self.endpoint_service.endpoints_count() == 0
        self.endpoint_service.get_endpoints()
        assert self.endpoint_service.endpoints_count() > 0

    def test_get_endpoint(self):
        endpoints = []
        self.endpoint_service.reset()
        self.endpoint_service.update_endpoints_list()
        for i in range(self.endpoint_service.endpoints_count()):
            endpoint = self.endpoint_service.get_endpoint()
            endpoints.append(endpoint)
        assert endpoints == self.endpoint_service.endpoints

        endpoint_url = self.endpoint_service.get_endpoint_url()
        expected_url = "http://" + self.endpoint_service.endpoints[0]['IP'] + ":" + self.endpoint_service.endpoints[0]['Port']
        assert endpoint_url == expected_url

    def test_get_endpoints_bad(self):
        config_sdk_servers_url = self.endpoint_service.config.sdk_servers_api
        config_endpoints = self.endpoint_service.config.endpoints
        self.endpoint_service.config.endpoints = json_parse("{\"Endpoints\": [{\"IP\": \"1.1.1.1\", \"Port\": \"8080\"}]}")
        self.endpoint_service.config.sdk_servers_api = 'http://not-exising-domain.xyz'
        self.endpoint_service.get_endpoints()
        assert not self.endpoint_service.endpoints
        self.endpoint_service.config.sdk_servers_api = config_sdk_servers_url
        self.endpoint_service.config.endpoints = config_endpoints

    def test_thread_start_stop(self):
        self.endpoint_service.StartServiceThread()
        self.endpoint_service.StopServiceThread()
        assert self.endpoint_service.service_thread_on is False


