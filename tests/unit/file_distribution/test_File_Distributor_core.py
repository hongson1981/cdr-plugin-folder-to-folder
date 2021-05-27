import os
import sys
from unittest import TestCase
import pytest

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, folder_create, file_copy,folder_delete_all,file_delete,file_exists

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.file_distribution.File_Distributor import File_Distributor
from cdr_plugin_folder_to_folder.utils.testing.Temp_Config import Temp_Config
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.processing.File_Processing import File_Processing
from cdr_plugin_folder_to_folder.processing.Loops import Loops
from cdr_plugin_folder_to_folder.utils.testing.Direct_API_Server import Direct_API_Server
from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
    )

class test_File_Distributor(Temp_Config):

    def setUp(self) -> None:
        self.file_distributor = File_Distributor()

    pre_processor = None
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Direct_API_Server().setup()

        cls.hash_json      = Hash_Json()
        cls.test_data      = Test_Data()
        cls.test_file      = cls.test_data.image()
        cls.pre_processor  = Pre_Processor()
        #cls.pre_processor.clear_data_and_status_folders()
        cls.stage_1        = cls.pre_processor.process((cls.test_file,))
        cls.hash_json.save()
        cls.stage_2        = Loops().LoopHashDirectories()
        cls.test_folder    = os.path.join(FIXTURE_DIR, '2f854897a694773abc921e1b1549274ae6c6b1f117dc32f795aa28d563e6c33f')
        cls.test_file      = os.path.join(FIXTURE_DIR, 'test_file.pdf')
        cls.zip_name       = "test.zip"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.pre_processor.clear_data_and_status_folders()
        folder_delete_all(os.path.join(os.getcwd(), "zip_folder"))

    def test__init__(self):
        assert self.file_distributor.config             is   not None
        assert self.file_distributor.hd1_base_location  is   not None
        assert self.file_distributor.hd2_base_location  is   not None
        assert self.file_distributor.hd3_base_location  is   not None

    # def test_get_hd1_files(self):
    #     response=self.file_distributor.get_hd1_files(1)
    #     assert response  is not None
    #     assert os.path.exists(response)
    #
    # def test_get_hd3_files(self):
    #     response = self.file_distributor.get_hd3_files(1)
    #     assert response is not None
    #     assert os.path.exists(response)

    def test_get_hd2_status(self):
        response = self.file_distributor.get_hd2_status()
        assert response is not None
        assert os.path.exists(response)

    @pytest.mark.skip("this will fail if when no files exists in hd2/data)")
    def test_get_hd2_data(self):
        response = self.file_distributor.get_hd2_data(1)      # num_of_file = 1  , get 1 files
        assert response is not None
        assert os.path.exists(response)

        response = self.file_distributor.get_hd2_data(-1)     # num_of_file = -1 , get all files
        assert response is not None

        response = self.file_distributor.get_hd2_data(0)      # num_of_file = 0  , invalid
        assert response == 0

    def test_get_hd2_processed(self):
        response = self.file_distributor.get_hd2_processed(1)  # num_of_file = 1   , get 1 files
        assert response is not None

        response = self.file_distributor.get_hd2_processed(-1)  # num_of_file = -1 , get all files
        assert response is not None

        response = self.file_distributor.get_hd2_processed(0)   # num_of_file = 0   , invalid
        assert response == 0

    def test_prepare_zip(self):
        zip_name  =  self.zip_name

        response  = self.file_distributor.prepare_zip(self.test_file,zip_name)           # zip a file
        assert response == os.path.join(self.file_distributor.zip_folder, zip_name)
        assert file_exists(os.path.join(self.file_distributor.zip_folder, zip_name))

        file_delete(os.path.join(self.file_distributor.zip_folder, zip_name))

        response  = self.file_distributor.prepare_zip(self.test_folder, zip_name)        # zip a folder
        assert response == os.path.join(self.file_distributor.zip_folder, zip_name)
        assert file_exists(os.path.join(self.file_distributor.zip_folder, zip_name))

        file_delete(os.path.join(self.file_distributor.zip_folder, zip_name))

    def test_prepare_hd2_hash_folder_zip(self):
        zip_name  =  self.zip_name
        test_path_list=[self.test_folder]

        response  = self.file_distributor.prepare_hd2_hash_folder_zip(test_path_list, zip_name)
        assert response == os.path.join(self.file_distributor.zip_folder, zip_name)
        assert file_exists(os.path.join(self.file_distributor.zip_folder, zip_name))

        file_delete(os.path.join(self.file_distributor.zip_folder, zip_name))


