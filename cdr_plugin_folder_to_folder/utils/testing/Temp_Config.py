from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import file_delete
from osbot_utils.utils.Misc import random_text

from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.Logging_Process import start_logging, \
    process_all_log_entries_and_end_logging_process
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data


class Temp_Config(TestCase):
    config        = None
    log_worker    = None
    setup_testing = None
    storage       = None


    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_testing = Setup_Testing()
        cls.log_worker    = start_logging()
        cls.storage       = Storage()
        cls.config        = cls.storage.config
        from cdr_plugin_folder_to_folder.utils.Logging import log_info
        log_info(message='in Temp_Config')
        cls.setup_testing.set_config_to_temp_folder()

    @classmethod
    def tearDownClass(cls) -> None:
        process_all_log_entries_and_end_logging_process()               # allow all log messages to be captured
        cls.setup_testing.restore_config()
        cls.setup_testing   = None
        cls.storage         = None
        cls.config          = None

    @log_duration
    def add_test_files(self, count=5, text_size=10, execute_stage_1=False):
        added_files = []
        #random_blog = random_text(length=count*text_size)
        for i in range(1, count+1):
            text = random_text() + '_' * text_size                                          # much better performance than using random_text for the full string
            test_file = Test_Data().create_test_pdf(text=text, file_key=f"temp_file_{i}")
            added_files.append(self.storage.hd1_add_file(test_file))
            file_delete(test_file)
        if execute_stage_1:
            self.execute_stage_1()
        return added_files

    def execute_stage_1(self):
        pre_processor = Pre_Processor()
        return pre_processor.process_folder(pre_processor.storage.hd1())
