import os
import json
from dotenv import load_dotenv
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_not_exists, path_combine, folder_create, create_folder, temp_folder, \
    folder_exists

# todo: refactor the whole test files so that it all comes from temp folders (not from files in the repo)

from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing

DEFAULT_HD1_NAME         = 'hd1'
DEFAULT_HD2_NAME         = 'hd2'
DEFAULT_HD3_NAME         = 'hd3'
DEFAULT_HD2_TODO_NAME    = 'todo'
DEFAULT_HD2_STATUS_NAME  = 'status'
DEFAULT_HD2_PROCESSED_NAME      = 'processed'
DEFAULT_HD2_NOT_SUPPORTED_NAME  = 'not_supported'
DEFAULT_ROOT_FOLDER      = path_combine(__file__                , '../../../test_data/scenario-1' )
DEFAULT_HD1_LOCATION     = path_combine(DEFAULT_ROOT_FOLDER     , DEFAULT_HD1_NAME                )
DEFAULT_HD2_LOCATION     = path_combine(DEFAULT_ROOT_FOLDER     , DEFAULT_HD2_NAME                )
DEFAULT_HD3_LOCATION     = path_combine(DEFAULT_ROOT_FOLDER     , DEFAULT_HD3_NAME                )
DEFAULT_ELASTIC_HOST     = "es01"
DEFAULT_ELASTIC_PORT     = "9200"
DEFAULT_ELASTIC_SCHEMA   = "http"
DEFAULT_KIBANA_HOST      = "kib01"
DEFAULT_KIBANA_PORT      = "5601"
DEFAULT_THREAD_COUNT     = 10
DEFAULT_TEST_SDK         = 'gw-cloud-sdk-455649808.eu-west-1.elb.amazonaws.com'
#DEFAULT_TEST_SDK         = '52.213.74.78'
DEFAULT_ENDPOINT_PORT    = '8080'
DEFAULT_MINIO_ENDPOINT_PORT    = '8088'          # Minio version is using this port
DEFAULT_ENDPOINTS        = '{"Endpoints":[{"IP":"' + DEFAULT_TEST_SDK + '", "Port":"' + DEFAULT_ENDPOINT_PORT +'"}]}'
DEFAULT_SUPPORTED_FILE_TYPES = '.doc .dot .xls .xlt .xlm .ppt .pot .pps .docx .dotx .docm .dotm .xlsx .xltx .xlsm .xltm .pptx .potx .ppsx .pptm .potm .ppsm .pdf .jpeg .jpg .jpe .png .gif'
DEFUALT_SAVE_UNSUPPORTED_FILE_TYPES = True
DEFAULT_REQUEST_TIMEOUT  = 600
DEFAULT_REBUILD_ZIP      = True
DEFAULT_USE_DYNAMIC_ENDPOINTS = False
DEFAULT_SDK_SERVERS_API  = 'https://tmol8zkg3c.execute-api.eu-west-1.amazonaws.com/prod/sdk-servers/ip_addresses'
DEFAULT_PROMETHEUS_HOST  = '127.0.0.1'
DEFAULT_PROMETHEUS_PORT  = '8000'
API_VERSION              = os.getenv    ("CDR_VERSION"     , "unknown"    )



class Config:
    _instance = None
    def __new__(cls):                                               # singleton pattern
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'root_folder') is False:                     # only set these values first time around
            self.hd1_location           = None
            self.hd2_location           = None
            self.hd2_todo_location      = None
            self.hd2_status_location    = None
            self.hd2_processed_location = None
            self.hd3_location           = None
            self.root_folder            = None
            self.elastic_host           = None
            self.elastic_port           = None
            self.elastic_schema         = None
            self.kibana_host            = None
            self.kibana_port            = None
            self.thread_count           = None
            self.test_sdk               = None
            self.endpoints              = None
            self.endpoints_count        = None
            self.request_timeout        = None
            self.use_rebuild_zip        = None
            self.sdk_servers_api        = None
            self.supported_file_types   = None
            self.save_unsupported_file_types = None
            self.use_dynamic_endpoints  = None
            self.prometheus_host        = None
            self.prometheus_port        = None
            self.prometheus_url         = None
            self.load_values()                                      # due to the singleton pattern this will only be executed once

    def load_values(self):
        Setup_Testing().set_test_root_dir()                         # todo: fix test data so that we don't need to do this here
        load_dotenv(override=True)                                  # Load configuration from .env file that should exist in the root of the repo
        self.root_folder         = os.getenv    ("ROOT_FOLDER"     , DEFAULT_ROOT_FOLDER    )
        self.elastic_host        = os.getenv    ("ELASTIC_HOST"    , DEFAULT_ELASTIC_HOST   )
        self.elastic_port        = os.getenv    ("ELASTIC_PORT"    , DEFAULT_ELASTIC_PORT   )
        self.elastic_schema      = os.getenv    ("ELASTIC_SCHEMA"  , DEFAULT_ELASTIC_SCHEMA )
        self.kibana_host         = os.getenv    ("KIBANA_HOST"     , DEFAULT_KIBANA_HOST    )
        self.kibana_port         = os.getenv    ("KIBANA_PORT"     , DEFAULT_KIBANA_PORT    )
        self.thread_count        = os.getenv    ("THREAD_COUNT"    , DEFAULT_THREAD_COUNT   )
        self.request_timeout     = os.getenv    ("REQUEST_TIMEOUT" , DEFAULT_REQUEST_TIMEOUT)
        self.use_rebuild_zip     = os.getenv    ("REBUILD_ZIP"     , DEFAULT_REBUILD_ZIP    )
        self.test_sdk            = os.getenv    ("TEST_SDK"        , DEFAULT_TEST_SDK       )
        self.sdk_servers_api     = os.getenv    ("SDK_SERVERS_API" , DEFAULT_SDK_SERVERS_API)
        self.use_dynamic_endpoints = os.getenv  ("USE_DYNAMIC_ENDPOINTS" , DEFAULT_USE_DYNAMIC_ENDPOINTS)

        json_string          = os.getenv("ENDPOINTS", DEFAULT_ENDPOINTS)
        self.endpoints       = json.loads(json_string)

        self.endpoints_count = len(self.endpoints['Endpoints'])

        file_types      = os.getenv("SUPPORTED_FILE_TYPES", DEFAULT_SUPPORTED_FILE_TYPES)
        self.supported_file_types = file_types.split()

        self.save_unsupported_file_types = os.getenv("SAVE_UNSUPPORTED_FILE_TYPES", DEFUALT_SAVE_UNSUPPORTED_FILE_TYPES)

        self.set_hd1_location(os.getenv("HD1_LOCATION", DEFAULT_HD1_LOCATION))       # set hd1, hd2 and hd3 values
        self.set_hd2_location(os.getenv("HD2_LOCATION", DEFAULT_HD2_LOCATION))
        self.set_hd3_location(os.getenv("HD3_LOCATION", DEFAULT_HD3_LOCATION))

        # Prometheus settings

        self.prometheus_host = os.getenv("PROMETHEUS_HOST", DEFAULT_PROMETHEUS_HOST)
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", DEFAULT_PROMETHEUS_PORT))
        self.prometheus_url = f'http://{self.prometheus_host}:{self.prometheus_port}'

        return self

    def ensure_last_char_is_not_forward_slash(self, path: str):
        if path.endswith('/') or path.endswith('\\'):
            path = path[:-1]
        return path

    def set_hd1_location(self, hd1_location):
        self.hd1_location = self.ensure_last_char_is_not_forward_slash(hd1_location)
        folder_create(self.hd1_location)

    def set_hd2_location(self, hd2_location):
        self.hd2_location           = self.ensure_last_char_is_not_forward_slash(hd2_location)
        self.hd2_todo_location      = path_combine(self.hd2_location, DEFAULT_HD2_TODO_NAME)
        self.hd2_status_location    = path_combine(self.hd2_location, DEFAULT_HD2_STATUS_NAME)
        self.hd2_processed_location     = path_combine(self.hd2_location, DEFAULT_HD2_PROCESSED_NAME)
        self.hd2_not_supported_location = path_combine(self.hd2_location, DEFAULT_HD2_NOT_SUPPORTED_NAME)
        folder_create(self.hd2_location       )
        folder_create(self.hd2_todo_location  )
        folder_create(self.hd2_status_location)
        folder_create(self.hd2_processed_location)

    def set_hd3_location(self, hd3_location):
        self.hd3_location = self.ensure_last_char_is_not_forward_slash(hd3_location)
        folder_create(self.hd3_location)


    def set_root_folder(self, root_folder=None):
        if folder_not_exists(root_folder):                                   # use temp folder if no value is provided or folder doesn't exist
            root_folder = temp_folder()

        self.root_folder = root_folder
        self.hd1_location = path_combine(root_folder, DEFAULT_HD1_NAME)      # set default values for h1, h2 and hd3
        self.hd2_location = path_combine(root_folder, DEFAULT_HD2_NAME)
        self.hd3_location = path_combine(root_folder, DEFAULT_HD3_NAME)

        self.set_hd1_location(self.hd1_location)                              # make sure folders exist
        self.set_hd2_location(self.hd2_location)
        self.set_hd3_location (self.hd3_location)
        return self

    def values(self):
        return {
            "hd1_location"           : self.hd1_location        ,
            "hd2_location"           : self.hd2_location        ,
            "hd2_todo_location"      : self.hd2_todo_location   ,
            "hd2_status_location"    : self.hd2_status_location ,
            "hd2_processed_location" : self.hd2_processed_location,
            "hd3_location"           : self.hd3_location        ,
            "root_folder"            : self.root_folder         ,
            "elastic_host"           : self.elastic_host        ,
            "elastic_port"           : self.elastic_port        ,
            "elastic_schema"         : self.elastic_schema      ,
            "kibana_host"            : self.kibana_host         ,
            "kibana_port"            : self.kibana_port         ,
            "thread_count"           : self.thread_count        ,
            "endpoints"              : self.endpoints           ,
            "request_timeout"        : self.request_timeout
        }
