import os
import sys
from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, folder_create, file_copy

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.processing.Loops import Loops
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

from cdr_plugin_folder_to_folder.api.routes.Processing import process_single_file
from cdr_plugin_folder_to_folder.api.routes.Processing import process_hd2_data_to_hd3
from cdr_plugin_folder_to_folder.api.routes.Processing import process_hd2_data_to_hd3_sequential
from cdr_plugin_folder_to_folder.api.routes.Processing import get_the_processing_status
from cdr_plugin_folder_to_folder.api.routes.Processing import get_prometheus_metrics

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

#todo add a lot more tests, namely the tests that are currently preventing the file from being correctly processed
class test_Processor(TestCase):
    pre_processor = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_data = Test_Data()
        cls.test_file = cls.test_data.image()
        cls.pre_processor = Pre_Processor()
        cls.pre_processor.clear_data_and_status_folders()
        cls.stage_1 = cls.pre_processor.process((cls.test_file,))
        # todo: add method to also delete hd3 output

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     cls.pre_processor.clear_data_and_status_folders()

    def setUp(self) -> None:
        self.config         = Config()
        self.repotrs_path   = os.path.join(self.config.hd2_location,"reports")
        self.processed_path = os.path.join(self.config.hd2_location,self.config.hd2_processed_location)
        self.pre_processor = Pre_Processor()
        self.loops         = Loops()

    def tearDown(self) -> None:
        pass

    def test__init__(self):
        self.pre_processor.clear_data_and_status_folders()       # clear output folders
        self.pre_processor.process_files()                       # copy files across

        assert folder_exists(self.config.hd1_location)
        assert folder_exists(self.config.hd2_location)
        assert folder_exists(self.config.hd3_location)

    def test_flags(self):
        assert self.loops.IsProcessing() == False
        self.loops.StopProcessing()
        assert self.loops.HasBeenStopped() == True

    @log_duration
    def test_process_file(self):
        assert ("File has been processed" == process_single_file())
        assert len(os.listdir(self.config.hd3_location)) != 0

    @log_duration
    def test_process_files(self):
        assert ("Loop completed" == process_hd2_data_to_hd3())
        assert len(os.listdir(self.config.hd3_location)) != 0

    @log_duration
    def test_process_files_sequential(self):
        assert ("Loop completed" == process_hd2_data_to_hd3_sequential())
        assert len(os.listdir(self.config.hd3_location)) != 0

    @log_duration
    def test_processing_inprogress(self):
        Loops.processing_started = True
        assert (False == self.loops.ProcessSingleFile())
        assert (False == self.loops.LoopHashDirectories())
        assert self.loops.ProcessSingleFile() is False
        assert self.loops.LoopHashDirectories() is False

    @log_duration
    def test_get_the_processing_status(self):
        response = get_the_processing_status()
        assert (response.headers['content-type'] == 'application/json')

    @log_duration
    def test_get_prometheus_metrics(self):
        response = get_prometheus_metrics()
        assert (response.headers['content-type'] == 'text/plain; charset=utf-8')
