import asyncio
from unittest import TestCase
from unittest.mock import patch

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import file_contents_as_bytes, folder_exists

from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json
from cdr_plugin_folder_to_folder.processing.File_Processing import File_Processing
from cdr_plugin_folder_to_folder.processing.Loops import Loops
from cdr_plugin_folder_to_folder.utils.Logging import log_info, log_debug
from cdr_plugin_folder_to_folder.utils.Logging_Process import start_logging
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
from cdr_plugin_folder_to_folder.utils.testing.Temp_Config import Temp_Config
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data
from cdr_plugin_folder_to_folder.pre_processing.Status import FileStatus

class test_Loops(Temp_Config):

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
        self.loops = Loops()

    def test_LoopHashDirectories(self):
        assert self.loops.LoopHashDirectories() is True
        #log_debug(message='stop_logging', data={'when': 'now'})
        #self.log_worker.join()

    def test_LoopHashDirectoriesAsync(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.loops.LoopHashDirectoriesAsync(thread_count=1))

    def test_updateHashJson(self):
        Loops.continue_processing = True
        count = 20
        self.add_test_files(count=count, execute_stage_1=True)

        json_data = self.loops.updateHashJson()
        assert len(json_data) > 0

    def test_moveProcessedFiles(self):
        Loops.continue_processing = True
        count = 20
        self.add_test_files(count=count, execute_stage_1=True)

        json_data = self.loops.updateHashJson()
        assert len(json_data) > 0

        self.loops.moveProcessedFiles()
        assert folder_exists(self.loops.storage.hd2_processed())

    def test_LoopHashDirectoriesInternal(self):
        Loops.continue_processing = True
        count = 20
        self.add_test_files(count=count, execute_stage_1=True)

        with patch.object(File_Processing, 'do_rebuild', return_value=True):
            self.loops.LoopHashDirectoriesInternal(thread_count=10, do_single=False)

        Loops.continue_processing = False

        metadatas = self.storage.hd2_metadatas()
        # whatever remains in 'data' folder has failed
        for metadata in metadatas:
            assert metadata.get('rebuild_status') ==  FileStatus.FAILED

        metadatas = self.storage.hd2_processed_metadatas()
        # whatever remains in 'processed' folder has completed successfully
        for metadata in metadatas:
            assert metadata.get('rebuild_status') ==  FileStatus.COMPLETED

        #metadata = metadatas[0]
        #hd3_file = hd3_files[0]

        #assert result is True
        #assert len(hd3_files) == count
        #assert len(metadatas) == count
        #assert b'Glasswall Processed' in file_contents_as_bytes(hd3_file)
        #assert metadata.get('rebuild_status') == 'Completed Successfully'

    def test_ProcessDirectoryWithEndpoint_bad(self):
        itempath = '/not_existing'
        filehash = '1234567890'
        assert self.loops.ProcessDirectoryWithEndpoint(itempath, filehash, 0) is False

    def test_LoopHashDirectoriesInternal_bad(self):
        hd2_todo_location = self.loops.config.hd2_todo_location
        self.loops.config.hd2_todo_location = '/not_existing'
        assert self.loops.LoopHashDirectoriesInternal(thread_count=30, do_single=False) is False
        self.loops.config.hd2_todo_location = hd2_todo_location



