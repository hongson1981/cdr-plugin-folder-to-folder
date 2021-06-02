import os
import requests
import zipfile
import shutil
import logging as logger
from datetime import datetime

from osbot_utils.utils.Files import folder_create, folder_delete_all, folder_copy, \
    path_combine, file_delete, file_exists, folder_exists

from cdr_plugin_folder_to_folder.common_settings.Config import Config, DEFAULT_THREAD_COUNT
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration

from cdr_plugin_folder_to_folder.pre_processing.Processing_Status import Processing_Status
from cdr_plugin_folder_to_folder.pre_processing.Status import Status, FileStatus

from cdr_plugin_folder_to_folder.processing.Analysis_Json import Analysis_Json
from cdr_plugin_folder_to_folder.processing.Events_Log import Events_Log
from cdr_plugin_folder_to_folder.metadata.Metadata import DEFAULT_REPORT_FILENAME
from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json

from cdr_plugin_folder_to_folder.metadata.Metadata_Elastic import Metadata_Elastic
from cdr_plugin_folder_to_folder.processing.Analysis_Elastic import Analysis_Elastic

import threading
from multiprocessing.pool import ThreadPool

logger.basicConfig(level=logger.INFO)

class Minio_Sync:

    lock = threading.Lock()

    def __init__(self):
        self.config         = Config()
        self.meta_service   = Metadata_Service()
        self.status         = Status()
        self.storage        = Storage()

    def mount_minio_bucket_as_hd2(self, url, user, access_token, bucket):
        retvalue = "No value"
        return retvalue
