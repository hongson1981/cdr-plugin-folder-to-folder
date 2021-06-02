from unittest import TestCase
import json

import pytest

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils.testing.Temp_API_Server import Temp_API_Server
from jupyter.notebooks.jupyter_apis.API_Client import API_Client

class test_API_Client(TestCase):
    api_server = None
    url_server = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.api_server = Temp_API_Server()
        cls.api_server.start_server()
        cls.url_server = cls.api_server.server_url()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.api_server.stop_server()

    def setUp(self):
        self.client = API_Client(url_server=self.url_server)


    def test__resolve_url(self):
        assert self.client._resolve_url('aaa' ) == f"{self.url_server}/aaa"
        assert self.client._resolve_url(''    ) == f"{self.url_server}"
        assert self.client._resolve_url(None  ) == f"{self.url_server}"
        assert self.client._resolve_url(      ) == f"{self.url_server}"
        assert self.client._resolve_url('/a'  ) == f"{self.url_server}/a"
        assert self.client._resolve_url('/a/b') == f"{self.url_server}/a/b"
        assert self.client._resolve_url('a/b' ) == f"{self.url_server}/a/b"

        self.client.server_ip += '/'

        assert self.client.server_ip == self.url_server + '/'
        assert self.client._resolve_url('aaa') == f"{self.url_server}/aaa"
        assert self.client._resolve_url(     ) == f"{self.url_server}/"
        assert self.client._resolve_url(''   ) == f"{self.url_server}/"
        assert self.client._resolve_url('///') == f"{self.url_server}/"

        self.client.server_ip += '/'

        assert self.client.server_ip == self.url_server + '//'                      # note: cases when two // in the server_ip cause some side effects
        assert self.client._resolve_url('aaa') == f"{self.url_server}/aaa"          # ok here
        assert self.client._resolve_url(     ) == f"{self.url_server}//"            # not ok here
        assert self.client._resolve_url(''   ) == f"{self.url_server}//"            # and here

        self.client.server_ip += '/123'

        assert self.client.server_ip == self.url_server + '///123'                  # when there is an extra segment
        assert self.client._resolve_url('aaa') == f"{self.url_server}/aaa"          # it is removed here
        assert self.client._resolve_url(''   ) == f"{self.url_server}///123"        # but it shows up here

    def test_health(self):
        result = self.client.health()
        assert result['status'] == 'ok'

    # def test_file_distributor_hd1(self):
    #     num_of_files = 1
    #     result = self.client.file_distributor_hd1(num_of_files)
    #     pprint(result)

    def test_version(self):
        result = self.client.version()
        assert result['version'] == Config().api_version

    @pytest.mark.skip("this is changing live data (this needs to run on a temp server path)")
    def test_configure_environment(self):
        data = { "hd1_path"  : "./test_data/scenario-1/hd1",
                 "hd2_path"  : "./test_data/scenario-1/hd2",
                 "hd3_path"  : "./test_data/scenario-1/hd3"}

        response=self.client.configure_environment(data=data)
        assert response.status_code is 200
        assert response.json() == data

    @pytest.mark.skip("this is breaking current .env file (this needs to run on a temp .env file)")
    def test_set_gw_sdk_endpoints(self):

        data = { "Endpoints": [{ "IP": "91.109.25.70", "Port": "8080" } ] }
        response = self.client.set_gw_sdk_endpoints(data=data)

        assert response.status_code == 200
        assert response.json() == data

    def test_get_processing_status(self):
        status = self.client.get_processing_status()
        assert status                 is not None
        assert "files_in_hd1_folder"  in status
        assert "files_to_process"     in status
        assert "completed"            in status
        assert "failed"               in status
        assert "in_progress"          in status


