import os
import pytest

from unittest import TestCase
from unittest.mock import patch

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import temp_folder, folder_files, folder_delete_all, folder_create, file_create_bytes, \
    file_contents_as_bytes, file_contents, file_name, temp_file, file_sha256, path_combine, file_exists, folder_exists
from osbot_utils.utils.Http import POST, POST_json
from osbot_utils.utils.Json import json_to_str, str_to_json
from osbot_utils.utils.Misc import base64_to_str, base64_to_bytes, str_to_bytes, random_string, random_text, \
    str_to_base64, bytes_to_str, bytes_to_base64, random_uuid

from osbot_utils.utils.Json import str_to_json, json_to_str, json_parse
from cdr_plugin_folder_to_folder.common_settings.Config import Config, DEFAULT_ENDPOINTS
from cdr_plugin_folder_to_folder.metadata.Metadata import Metadata
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.metadata.Metadata_Utils import Metadata_Utils
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.processing.Endpoint_Service import Endpoint_Service
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
from cdr_plugin_folder_to_folder.pre_processing.Status import FileStatus
from cdr_plugin_folder_to_folder.configure.Configure_Env import SDKEngineVersionKey, SDKAPIVersionKey
import traceback
import base64

class test_File_Processing(Temp_Config):

    config    = None
    temp_root = None

    # @classmethod
    # def setUpClass(cls) -> None:
    #     super().setUpClass()
    #
    #     #cls.temp_root       = folder_create('/tmp/temp_root') # temp_folder()
    #     #cls.config.set_root_folder(root_folder=cls.temp_root)

    def setUp(self) -> None:
        self.sdk_server         = self.config.test_sdk
        self.sdk_port           = '8080'
        #self.temp_folder        = temp_folder()
        self.events_elastic     = Events_Log_Elastic()
        self.endpoint_service   = Endpoint_Service()
        self.report_elastic     = Report_Elastic()
        self.analysis_elastic   = Analysis_Elastic()
        self.storage            = Storage()
        self.meta_service       = Metadata_Service()
        self.test_file_path     = self.add_test_files(count=1, execute_stage_1=True).pop()  # Test_Data().create_test_pdf(text=random_text(prefix="some random text: "))
        self.test_file_name     = file_name(self.test_file_path)
        self.test_file_hash     = self.storage.hd2_data_file_hashes().pop()
        self.test_file_metadata = Metadata(file_hash=self.test_file_hash).load()
        self.events_log         = self.test_file_metadata.events_log()
        self.file_processing    = File_Processing(events_log=self.events_log, events_elastic = self.events_elastic, report_elastic=self.report_elastic, analysis_elastic= self.analysis_elastic, meta_service=self.meta_service )
        assert self.test_file_metadata.exists()
        #assert self.test_file_metadata.get_original_file_paths() == [self.test_file_name]

    def tearDown(self) -> None:

        self.test_file_metadata.delete()

    def test_do_rebuild_zip(self):

        self.endpoint_service.endpoints = str_to_json(DEFAULT_ENDPOINTS)["Endpoints"]

        endpoint = self.endpoint_service.get_endpoint_url()
        metadata = self.test_file_metadata
        folder_path = metadata.metadata_folder_path()
        source_path = metadata.source_file_path()

        kwargs = {"endpoint": endpoint,
                  "hash": self.test_file_hash,
                  "source_path": source_path,
                  "dir": folder_path}

        assert self.file_processing.do_rebuild_zip(**kwargs)

        metadata.load()
        #assert metadata.data.get('xml_report_status'      ) == 'Obtained'
        #assert metadata.data.get('file_name'              ) == self.test_file_name
        assert metadata.data.get('rebuild_server'         ) == endpoint
        assert metadata.data.get('server_version'         ) == 'Engine:1.157 API:0.1.15'
        assert metadata.data.get('error'                  ) is None
        assert metadata.data.get('original_hash'          ) == self.test_file_hash
        assert metadata.data.get('original_file_size'     ) == 755
        assert metadata.data.get('original_file_extension') == '.pdf'
        assert metadata.data.get('rebuild_status'         ) == 'Initial'
        assert metadata.data.get('rebuild_file_extension' ) == 'pdf'
        assert metadata.data.get('rebuild_file_size'      ) == 1267


    def test_do_rebuild(self):

        self.endpoint_service.endpoints = str_to_json(DEFAULT_ENDPOINTS)["Endpoints"]

        endpoint = self.endpoint_service.get_endpoint_url()
        metadata = self.test_file_metadata
        folder_path = metadata.metadata_folder_path()
        source_path = metadata.source_file_path()


        kwargs = {"endpoint"    : endpoint              ,
                  "hash"        : self.test_file_hash   ,
                  "source_path" : source_path           ,
                  "dir"         : folder_path           }

        assert self.file_processing.do_rebuild(**kwargs)

        pprint(metadata.load())

        assert metadata.data.get('xml_report_status'      ) == 'Obtained'
        assert metadata.data.get('file_name'              ) == self.test_file_name
        assert metadata.data.get('rebuild_server'         ) == endpoint
        assert metadata.data.get('server_version'         ) == 'Engine:1.157 API:0.1.15'
        assert metadata.data.get('error'                  ) is None
        assert metadata.data.get('original_hash'          ) == self.test_file_hash
        assert metadata.data.get('original_file_size'     ) == 755
        assert metadata.data.get('original_file_extension') == '.pdf'
        assert metadata.data.get('rebuild_status'         ) == 'Initial'
        assert metadata.data.get('rebuild_file_extension' ) == 'pdf'
        assert metadata.data.get('rebuild_file_size'      ) == 1267

    def test_processDirectory(self):
        self.endpoint_service.endpoints = str_to_json(DEFAULT_ENDPOINTS)["Endpoints"]

        endpoint    = self.endpoint_service.get_endpoint_url()
        metadata    = self.test_file_metadata
        folder_path = metadata.metadata_folder_path()
        source_path = metadata.source_file_path()

        kwargs = {"endpoint"    : endpoint              ,
                  "dir"         : folder_path           }

        assert self.file_processing.processDirectory(**kwargs)


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

    def test_processBadFile(self):
        bad_file = temp_file(contents=random_text())
        metadata = self.meta_service.create_metadata(bad_file)
        endpoint = f'http://{self.sdk_server}:{self.sdk_port}'
        dir = metadata.metadata_folder_path()
        try:
            result = self.file_processing.processDirectory(endpoint=endpoint, dir=dir)
        except Exception as e:
            traceback.print_exc()
            self.fail("Should not have thrown")
        assert result == True
        metadata.load()
        assert metadata.data.get('rebuild_status') == FileStatus.NOT_SUPPORTED


    def test_processBadFileWithoutSaveOriginal(self):
        bad_file = temp_file(contents=random_text())
        self.config.save_unsupported_file_types = False
        metadata = self.meta_service.create_metadata(bad_file)
        endpoint = f'http://{self.sdk_server}:{self.sdk_port}'
        dir = metadata.metadata_folder_path()
        try:
            result = self.file_processing.processDirectory(endpoint=endpoint, dir=dir)
        except Exception as e:
            traceback.print_exc()
            self.fail("Should not have thrown")
        assert result == True
        metadata.load()
        assert metadata.data.get('rebuild_status') == FileStatus.NOT_SUPPORTED

    def test_pdf_rebuild(self):            # refactor into separate test file
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


    def test_processDirectory__bad_zip_file(self):
        bad_file = temp_file(contents=random_text())
        metadata = self.meta_service.create_metadata(bad_file)
        endpoint = f'http://{self.sdk_server}:{self.sdk_port}'
        dir = metadata.metadata_folder_path()
        result = self.file_processing.processDirectory(endpoint=endpoint, dir=dir, use_rebuild_zip=True)
        assert result == True
        metadata.load()
        assert metadata.data.get('rebuild_status') == FileStatus.NOT_SUPPORTED
        assert metadata.data.get('error')          == "Error while processing the request. See details in \'error.json\'"

    def test_processZipFileWithDualEP(self):
        uuid = random_text()
        path = '/tmp/'+uuid
        zip_file = Test_Data().create_test_zip(path=path)
        metadata = self.meta_service.create_metadata(zip_file)
        endpoint = f'http://{self.sdk_server}:{self.sdk_port}'
        dir = metadata.metadata_folder_path()
        try:
            result = self.file_processing.processDirectory(endpoint=endpoint, dir=dir, use_rebuild_zip=True)
        except Exception as e:
            traceback.print_exc()
            self.fail("Should not have thrown")
        #assert result == True
        metadata.load()
        assert metadata.data.get('rebuild_status') == FileStatus.NOT_SUPPORTED

    def test_zbase64request_with_wrong_endpoint(self):
        with pytest.raises(ValueError):
            self.file_processing.base64request("no-endpoint","no-route","ABC")

    def test_xmlreport_request_with_wrong_endpoint(self):
        with pytest.raises(ValueError):
            self.file_processing.xmlreport_request("no-endpoint","ABC")

    def test_zconvert_xml_report_to_json_with_no_xmlreport(self):
        with pytest.raises(ValueError):
            self.file_processing.convert_xml_report_to_json("/", None)

    def test_zconvert_xml_report_to_json_with_bad_xmlreport(self):
        xmlreport = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>  \
                        <note>  \
                        <to>Tove</to>  \
                        <from>Jani</from>  \
                        <heading>Reminder</heading>  \
                        <body>Don't forget me this weekend!</body>  \
                        </note> \
                    "
        assert self.file_processing.convert_xml_report_to_json("/", xmlreport) is False

    def test_do_rebuild_with_bad_source_path(self):
        metadata_file_path = self.test_file_metadata.metadata_file_path()
        assert self.file_processing.do_rebuild('none','none','/',os.path.dirname(metadata_file_path)) is False

    @patch('cdr_plugin_folder_to_folder.processing.File_Processing.File_Processing.rebuild')
    def test_do_rebuild_with_empty_response(self, mock_rebuild):
        mock_rebuild.return_value.ok = True
        dir = os.path.dirname(self.test_file_metadata.metadata_file_path())
        source = path_combine(dir,"source")
        endpoint = 'http://127.0.0.1:8000'
        assert self.file_processing.do_rebuild(endpoint,'ABC',source,dir) is False

    def test_get_server_version(self):

        headers = {SDKEngineVersionKey: '1.0.0', SDKAPIVersionKey: '1.0.0'}
        assert SDKEngineVersionKey in headers
        assert SDKAPIVersionKey in headers

        dir = os.path.dirname(self.test_file_metadata.metadata_file_path())
        self.file_processing.get_server_version(dir, headers)
        server_version = self.file_processing.meta_service.metadata.get_server_version()
        assert server_version == 'Engine:1.0.0 API:1.0.0'

        headers = {}
        assert not SDKEngineVersionKey in headers
        assert not SDKAPIVersionKey in headers

        self.file_processing.get_server_version(dir, headers)
        server_version = self.file_processing.meta_service.metadata.get_server_version()
        assert server_version == 'Engine:1.0.0 API:1.0.0'
