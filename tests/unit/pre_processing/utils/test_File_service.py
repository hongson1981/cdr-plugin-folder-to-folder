import os
import shutil
from unittest import TestCase

from osbot_utils.utils.Files import folder_exists, temp_folder, file_exists, folder_temp, folder_delete_all, temp_file, \
    file_copy, create_folder

from cdr_plugin_folder_to_folder.pre_processing.utils.file_service import File_Service
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

class test_File_service(TestCase):
    #test_folder="./test_data/test_files"
    #new_folder=os.path.join(test_folder, "sample")
    new_folder = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.new_folder = temp_folder()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.new_folder)
        pass

    def setUp(self) -> None:
        self.test_data    = Test_Data()
        self.file_service = File_Service()
        self.test_folder  = self.test_data.path_test_files
        self.test_file    = self.test_data.image()
        self.dict_content = { "value": "testing" }

    def test_wrtie_json_file(self):
        create_folder(self.new_folder)
        self.file_service.wrtie_json_file(self.new_folder,"test.json",self.dict_content)

        assert os.path.exists(os.path.join(self.new_folder,"test.json")) is True

    def test_read_json_file(self):
        json_file_path=self.test_data.json()
        content=self.file_service.read_json_file(json_file_path)

        assert content is not None





