import asyncio
from unittest import TestCase
from unittest.mock import patch

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import file_contents_as_bytes, folder_exists

#from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json
#from cdr_plugin_folder_to_folder.processing.File_Processing import File_Processing
#from cdr_plugin_folder_to_folder.processing.Loops import Loops
#from cdr_plugin_folder_to_folder.utils.Logging import log_info, log_debug
#from cdr_plugin_folder_to_folder.utils.Logging_Process import start_logging
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
from cdr_plugin_folder_to_folder.utils.testing.Temp_Config import Temp_Config
#from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
#from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data
#from cdr_plugin_folder_to_folder.pre_processing.Status import FileStatus
from cdr_plugin_folder_to_folder.processing.Endpoint_Service import Endpoint_Service


class test_Endpoint_Service(Temp_Config):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        #cls.test_data = Test_Data()
        #cls.test_file = cls.test_data.image()
        #cls.pre_processor = Pre_Processor()
        #cls.pre_processor.clear_data_and_status_folders()
        #cls.stage_1 = cls.pre_processor.process(cls.test_file)
        pass

    def setUp(self) -> None:
        Setup_Testing()
        self.endpoint_service = Endpoint_Service()

    def test_get_endpoints(self):
        self.endpoint_service.reset()
        assert self.endpoint_service.endpoints_count() == 0
        self.endpoint_service.get_endpoints()
        assert self.endpoint_service.endpoints_count() > 0

    def test_get_endpoint(self):
        endpoints = []
        self.endpoint_service.get_endpoints()
        for i in range(self.endpoint_service.endpoints_count()):
            endpoint = self.endpoint_service.get_endpoint()
            endpoints.append(endpoint)
        assert endpoints == self.endpoint_service.endpoints

    def test_get_endpoints_bad(self):
        config_sdk_servers_url = self.endpoint_service.config.sdk_servers_api
        self.endpoint_service.config.sdk_servers_api = 'http://not-exising-domain.xyz'
        self.endpoint_service.get_endpoints()
        assert len(self.endpoint_service.endpoints) > 0
        self.endpoint_service.config.sdk_servers_api = config_sdk_servers_url


