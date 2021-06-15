import json
from unittest import TestCase, mock

import dotenv
import pytest

from osbot_utils.utils.Json import json_to_str
from osbot_utils.utils.Dev import pprint

from cdr_plugin_folder_to_folder.configure.Configure_Env import Configure_Env
from cdr_plugin_folder_to_folder.common_settings.Config import Config
from osbot_utils.utils.Files import folder_exists, folder_delete_all
from os import environ,path,remove,rename

from unittest.mock import patch,Mock

class test_Configure_Env(TestCase):

    def setUp(self) -> None:
        self.config = Config()
        self.configure = Configure_Env()

    @classmethod
    def setUpClass(cls) -> None:
        cls._dotenv_file=dotenv.find_dotenv()
        if cls._dotenv_file :
            rename(cls._dotenv_file ,path.join(path.dirname(cls._dotenv_file),".env_backup"))

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._dotenv_file:
            rename(path.join(path.dirname(cls._dotenv_file), ".env_backup"),cls._dotenv_file)

    def test_configure(self):
        hd1_path      = "./test_data/scenario-1/hd1"
        hd2_path      = "./test_data/scenario-1/hd2"
        hd3_path      = "./test_data/scenario-1/hd3"

        response=self.configure.configure(hd1_path=hd1_path,
                                          hd2_path=hd2_path,
                                          hd3_path=hd3_path)

        assert response is not None
        assert self.configure.last_error_message == ""
        self.assertEqual(environ["HD1_LOCATION"]   , hd1_path)
        self.assertEqual(environ["HD2_LOCATION"]   , hd2_path)
        self.assertEqual(environ["HD3_LOCATION"]   , hd3_path)

    def test_invalid_hd1(self):
        hd1_path      = "./test_data/scenario-1/hd1xyz"
        hd2_path      = "./test_data/scenario-1/hd2"
        hd3_path      = "./test_data/scenario-1/hd3"

        response=self.configure.configure(hd1_path=hd1_path,
                                          hd2_path=hd2_path,
                                          hd3_path=hd3_path)

        assert self.configure.last_error_message != ""
        assert response is not None

    def test_invalid_hd2(self):
        hd1_path      = "./test_data/scenario-1/hd1"
        hd2_path      = "./test_data/scenario-1/hd2xyz"
        hd3_path      = "./test_data/scenario-1/hd3"

        response=self.configure.configure(hd1_path=hd1_path,
                                          hd2_path=hd2_path,
                                          hd3_path=hd3_path)

        assert self.configure.last_error_message == ""
        assert response is not None
        assert folder_exists(hd2_path)
        folder_delete_all(hd2_path)

    def test_invalid_hd3(self):
        hd1_path      = "./test_data/scenario-1/hd1"
        hd2_path      = "./test_data/scenario-1/hd2"
        hd3_path      = "./test_data/scenario-1/hd3xyz"

        response=self.configure.configure(hd1_path=hd1_path,
                                          hd2_path=hd2_path,
                                          hd3_path=hd3_path)

        assert self.configure.last_error_message == ""
        assert response is not None
        assert folder_exists(hd3_path)
        folder_delete_all(hd3_path)

    # @pytest.mark.skip("this is breaking current .env file (this needs to run on a temp .env file)")
    @patch("cdr_plugin_folder_to_folder.configure.Configure_Env.Configure_Env.get_valid_endpoints")
    def test_configure_multiple_gw_sdk_endpoints(self,mock_get_valid_endpoints):

        endpoint_string                       = '{"Endpoints":[{"IP":"0.0.0.0", "Port":"8080"},{"IP":"0.0.0.1", "Port":"8080"}]}'
        expected_return_value                 = '{"Endpoints":[{"IP":"0.0.0.0", "Port":"8080"}]}'
        mock_get_valid_endpoints.return_value = expected_return_value

        old_endpoints        = self.config.endpoints
        old_endpoints_string  = json_to_str(old_endpoints)
        print(f'old_endpoint_string {old_endpoints_string}')
        response=self.configure.configure_endpoints(endpoint_string=endpoint_string)

        assert response is not None
        self.assertEqual(response   , json.loads(expected_return_value))

        mock_get_valid_endpoints.return_value = old_endpoints_string
        response=self.configure.configure_endpoints(endpoint_string=old_endpoints_string)
        assert response is not None

    @patch("cdr_plugin_folder_to_folder.configure.Configure_Env.Configure_Env.gw_sdk_health_and_version_check")
    def test_get_valid_endpoints(self,mock_gw_sdk_healthcheck):
        endpoint_string = '{"Endpoints":[{"IP":"0.0.0.0", "Port":"8080"}]}'

        mock_gw_sdk_healthcheck.return_value.status_code = 200
        response = self.configure.get_valid_endpoints(endpoint_string=endpoint_string)
        self.assertEqual(json.loads(response)  , json.loads(endpoint_string))

    def test_configure_invalid_endpoints(self):
        endpoint_string = '{"Endpoints":[{"IP":"0.0.0.0", "Port":"8080"}]}'
        assert self.configure.configure_endpoints(endpoint_string=endpoint_string) == -1

    @patch("requests.request")
    def test_gw_sdk_healthcheck(self,mock_request):
        mock_request.return_value.status_code=404

        server_url="http://0.0.0.1:8800"
        response = self.configure.gw_sdk_health_and_version_check(server_url)

        assert response is None

    # @patch("dotenv.find_dotenv")
    # def test_configure_with_exception(self,mock_find_dotenv):
    #     exception = IOError("File not found")
    #     mock_find_dotenv.get(mock.ANY).raise_for_status.side_effect = exception

    #     hd1_path      = "./test_data/scenario-1/hd1"
    #     hd2_path      = "./test_data/scenario-1/hd2"
    #     hd3_path      = "./test_data/scenario-1/hd3"

    #     with pytest.raises(IOError) as error_info:
    #         self.configure.configure (  hd1_path=hd1_path,
    #                                     hd2_path=hd2_path,
    #                                     hd3_path=hd3_path)
    #         assert error_info == exception









