from unittest import TestCase
from osbot_utils.utils.Files import file_exists
import pytest

from cdr_plugin_folder_to_folder.common_settings.Config import API_VERSION
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.processing.File_Processing import File_Processing
from cdr_plugin_folder_to_folder.processing.Loops import Loops
from cdr_plugin_folder_to_folder.utils.testing.Direct_API_Server import Direct_API_Server
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data
from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json


class test_File_Distributor(TestCase):
    pre_processor = None
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Direct_API_Server().setup()
        cls.prefix = 'file-distributor'

        cls.hash_json      = Hash_Json()
        cls.test_data      = Test_Data()
        cls.test_file      = cls.test_data.image()
        cls.pre_processor = Pre_Processor()
        cls.pre_processor.clear_data_and_status_folders()
        cls.stage_1       = cls.pre_processor.process((cls.test_file,))
        cls.hash_json.save()
        cls.stage_2       = Loops().LoopHashDirectories()
        #assert cls.stage_2 is True

    @classmethod
    def tearDownClass(cls) -> None:
        cls.pre_processor.clear_data_and_status_folders()

    # def test_hd1(self):
    #     num_of_files = 1
    #     path = f"{self.prefix}/hd1/{num_of_files}"
    #     response = self.client.GET_FILE(path)
    #     assert response.status_code is 200
    #     assert response.content is not None

    # def test_hd1(self):
    #     num_of_files = 1
    #     path = f"{self.prefix}/hd1/{num_of_files}"
    #     response = self.client.GET_FILE(path)
    #     assert response.status_code is 200
    #     assert response.content is not None
    #

    def test_hd2_status(self):
        path         = f"{self.prefix}/hd2/status"
        response = self.client.GET_FILE(path)
        assert response.status_code == 200
        assert response.content is not None

    @pytest.mark.skip("this will fail if when no files exists in hd2/data)")
    def test_get_hd2_data(self):
        num_of_files = 1
        path = f"{self.prefix}/hd2/data?num_of_files={num_of_files}"       # num_of_files = 1
        response = self.client.GET_FILE(path)                              # get 1 file
        assert response.status_code == 200
        assert response.content is not None

        path = f"{self.prefix}/hd2/data?num_of_files=-1"                    # num_of_files = -1
        response = self.client.GET_FILE(path)                               # get all files
        assert response.status_code == 200
        assert response.content is not None

        num_of_files = 0
        path = f"{self.prefix}/hd2/data?num_of_files={num_of_files}"        # num_of_files = 0, invalid
        response = self.client.GET_FILE(path)
        assert response.status_code == 403
        assert response.content.decode("utf-8") == "Invalid value for num_of_files"

    @pytest.mark.skip("this will fail if when no files exists in hd2/processed)")
    def test_get_hd2_processed(self):
        num_of_files = 1
        path = f"{self.prefix}/hd2/processed?num_of_files={num_of_files}"   # num_of_files = 1
        response = self.client.GET_FILE(path)                               #get 1 file
        assert response.status_code == 200
        assert response.content is not None

        path = f"{self.prefix}/hd2/processed?num_of_files=-1"               # num_of_files = -1
        response = self.client.GET_FILE(path)                               # get all files
        assert response.status_code == 200
        assert response.content is not None

        num_of_files = 0
        path = f"{self.prefix}/hd2/processed?num_of_files={num_of_files}"   # num_of_files = 0, invalid
        response = self.client.GET_FILE(path)
        assert response.status_code == 403
        assert response.content.decode("utf-8") == "Invalid value for num_of_files"

    # def test_hd3(self):
    #     num_of_files = 1
    #     path = f"{self.prefix}/hd3/{num_of_files}"
    #     response = self.client.GET_FILE(path)
    #     assert response.status_code is 200
    #     assert response.content is not None