from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import temp_folder, folder_files, folder_delete_all, folder_create, file_create_bytes, \
    file_contents_as_bytes, file_contents, file_name, temp_file, file_sha256
from osbot_utils.utils.Http import POST, POST_json
from osbot_utils.utils.Json import json_to_str
from osbot_utils.utils.Misc import base64_to_str, base64_to_bytes, str_to_bytes, random_string, random_text, \
    str_to_base64, bytes_to_str, bytes_to_base64

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.metadata.Metadata_Utils import Metadata_Utils
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.processing.Events_Log import Events_Log
from cdr_plugin_folder_to_folder.processing.Events_Log_Elastic import Events_Log_Elastic
from cdr_plugin_folder_to_folder.processing.File_Processing import File_Processing
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.utils.file_utils import FileService
from cdr_plugin_folder_to_folder.utils.testing.Temp_Config import Temp_Config
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data
from cdr_plugin_folder_to_folder.processing.Report_Elastic import Report_Elastic
from cdr_plugin_folder_to_folder.processing.Analysis_Json import Analysis_Json
from cdr_plugin_folder_to_folder.processing.Analysis_Elastic import Analysis_Elastic

class test_File_Processing(Temp_Config):

    config    = None
    temp_root = None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_file       = Test_Data().create_test_pdf(text=random_text(prefix="some random text: "))
        cls.test_file_name  = file_name(cls.test_file)
        cls.config          = Config()
        #cls.temp_root       = folder_create('/tmp/temp_root') # temp_folder()
        #cls.config.set_root_folder(root_folder=cls.temp_root)
        cls.meta_service    = Metadata_Service()
        cls.metadata        = cls.meta_service.create_metadata(cls.test_file)
        cls.analysis_json = Analysis_Json()


    # @classmethod
    # def tearDownClass(cls) -> None:
    #     super().tearDownClass()
    #     cls.config.load_values()                    # reset config values
    #     #folder_delete_all(cls.temp_root)

    def setUp(self) -> None:

        self.sdk_server      = self.config.test_sdk
        self.sdk_port        = '8080'
        self.temp_folder     = temp_folder()
        self.events_log      = Events_Log(self.temp_folder)
        self.events_elastic  = Events_Log_Elastic()
        self.report_elastic  = Report_Elastic()
        self.analysis_elastic = Analysis_Elastic()
        self.file_processing = File_Processing(events_log=self.events_log, events_elastic = self.events_elastic, report_elastic=self.report_elastic, analysis_elastic= self.analysis_elastic, meta_service=self.meta_service )
        self.storage         = Storage()

    def test_get_xmlreport(self):
        endpoint = ''
        headers = ''
        dir     = ''

    # todo move this test to integration tests and refactor test here to mock the server response
    def test_do_rebuild(self):          # refactor
        endpoint    = f'http://{self.sdk_server}:{self.sdk_port}'
        hash        = Metadata_Utils().file_hash(self.test_file)
        assert self.analysis_json.add_file(hash, self.test_file_name) is True
        dir         = self.metadata.metadata_folder_path()
        result = self.file_processing.do_rebuild(endpoint=endpoint, hash=hash, source_path=self.test_file, dir=dir)
        assert result is True
        assert self.metadata.metadata_file_exists()
        assert self.metadata.report_file_exists()

    def test_do_rebuild_bad_file(self):  # refactor
        bad_file      = temp_file(contents=random_text())
        file_hash     = file_sha256(bad_file)
        metadata      = self.meta_service.create_metadata(bad_file)
        endpoint    = f'http://{self.sdk_server}:{self.sdk_port}'
        dir         = metadata.metadata_folder_path()
        result      = self.file_processing.do_rebuild(endpoint=endpoint, hash=file_hash, source_path=bad_file, dir=dir)
        assert result == False
        metadata.load()
        assert metadata.data.get('error') ==  File_Processing.RESP_CODE_NOT_DECODED

    def test_processDirectory__bad_file(self):
        bad_file = temp_file(contents=random_text())
        metadata = self.meta_service.create_metadata(bad_file)
        endpoint = f'http://{self.sdk_server}:{self.sdk_port}'
        dir = metadata.metadata_folder_path()
        result = self.file_processing.processDirectory(endpoint=endpoint, dir=dir)
        assert result == False
        metadata.load()
        assert metadata.data.get('rebuild_status') == 'Completed with errors'
        assert metadata.data.get('error')          == File_Processing.RESP_CODE_NOT_DECODED

    def test_pdf_rebuild(self,):            # refactor into separate test file
        server          = self.config.test_sdk
        url             = f"http://{server}:8080/api/rebuild/base64"
        headers         = { 'accept': 'application/json',
                            'Content-Type': 'application/json'}
        text            = random_text("random text - ")
        test_pdf        = Test_Data().create_test_pdf(text=text)
        original_bytes  = file_contents_as_bytes(test_pdf)

        original_base64 = bytes_to_base64(original_bytes)
        post_data       = {"Base64": original_base64}
        result          = POST(url, data=post_data, headers=headers)
        rebuild_base64 = base64_to_bytes(result)

        assert str_to_bytes(text)     in     original_bytes
        assert b'Glasswall'           not in original_bytes

        assert str_to_bytes(text)     in     rebuild_base64
        assert b'Glasswall'           in     rebuild_base64
        #pprint(rebuild_base64)
        #assert b'Glasswall'    in     rebuild_base64



    # def test_server_status(self,):            # refactor into separate test file
    #     server         = "84.16.229.232"  # aws                                            # 5.1 lowest response time
    #     #server          = "192.168.0.249"   # local                                         # 3.9 lowest response time
    #     server          = "34.254.193.225"                                                 # 0.5 lowest response time
    #     server          = "CompliantK8sICAPLB-d6bf82358f9adc63.elb.eu-west-1.amazonaws.com"
    #     server          = "34.243.13.180"
    #     url             = f"http://{server}:8080/api/rebuild/base64"
    #     headers         = { 'accept': 'application/json',
    #                         'Content-Type': 'application/json'}
    #     text            = random_text("random text - ")
    #     test_pdf        = Test_Data().create_test_pdf(text=text)
    #     original_bytes  = file_contents_as_bytes(test_pdf)
    #
    #     original_base64 = bytes_to_base64(original_bytes)
    #     post_data       = {"Base64": original_base64}
    #     try:
    #         result = POST(url, data=post_data, headers=headers)
    #         rebuild_base64 = base64_to_bytes(result)
    #         pprint(rebuild_base64)
    #     except Exception as error:
    #         pprint(error)
    # #`

