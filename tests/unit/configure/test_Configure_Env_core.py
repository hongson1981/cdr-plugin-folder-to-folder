import json
from unittest import TestCase

import dotenv
import pytest

from cdr_plugin_folder_to_folder.configure.Configure_Env import Configure_Env
from os import environ,path,remove,rename

from unittest.mock import patch,Mock
class test_Configure_Env(TestCase):

    def setUp(self) -> None:
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

    @pytest.mark.skip("this is was failing in CI tests (todo: fix it)")
    def test_configure(self):
        hd1_path      = "./test_data/scenario-1/hd1"
        hd2_path      = "./test_data/scenario-1/hd2"
        hd3_path      = "./test_data/scenario-1/hd3"

        response=self.configure.configure(hd1_path=hd1_path,
                                          hd2_path=hd2_path,
                                          hd3_path=hd3_path)

        assert response is not None
        self.assertEqual(environ["HD1_LOCATION"]   , hd1_path)
        self.assertEqual(environ["HD2_LOCATION"]   , hd2_path)
        self.assertEqual(environ["HD3_LOCATION"]   , hd3_path)

    @pytest.mark.skip("this is breaking current .env file (this needs to run on a temp .env file)")
    @patch("cdr_plugin_folder_to_folder.configure.Configure_Env.Configure_Env.get_valid_endpoints")
    def test_configure_multiple_gw_sdk_endpoints(self,mock_get_valid_endpoints):

        endpoint_string                       = '{"Endpoints":[{"IP":"0.0.0.0", "Port":"8080"},{"IP":"0.0.0.1", "Port":"8080"}]}'
        expected_return_value                 = '{"Endpoints":[{"IP":"0.0.0.0", "Port":"8080"}]}'
        mock_get_valid_endpoints.return_value = expected_return_value
        response=self.configure.configure_endpoints(endpoint_string=endpoint_string)

        assert response is not None
        self.assertEqual(response   , json.loads(expected_return_value))

    @patch("cdr_plugin_folder_to_folder.configure.Configure_Env.Configure_Env.gw_sdk_healthcheck")
    def test_get_valid_endpoints(self,mock_gw_sdk_healthcheck):
        endpoint_string = '{"Endpoints":[{"IP":"0.0.0.0", "Port":"8080"}]}'

        response = self.configure.get_valid_endpoints(endpoint_string=endpoint_string)
        assert response is None

        mock_gw_sdk_healthcheck.return_value.status_code = 200
        response = self.configure.get_valid_endpoints(endpoint_string=endpoint_string)
        self.assertEqual(json.loads(response)  , json.loads(endpoint_string))

    @patch("requests.request")
    def test_gw_sdk_healthcheck(self,mock_request):
        mock_request.return_value.status_code=404

        server_url="http://0.0.0.1:8800"
        response = self.configure.gw_sdk_healthcheck(server_url)

        assert response is not None
        assert response.status_code == 404











