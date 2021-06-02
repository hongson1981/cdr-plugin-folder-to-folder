import os
import requests
import zipfile
import shutil
import logging as logger
from datetime import datetime

from osbot_utils.utils.Files import folder_create, folder_delete_all, folder_copy, \
    path_combine, file_delete, file_exists, folder_exists, temp_file

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

import importlib.util
import sys

logger.basicConfig(level=logger.INFO)

class Minio_Sync:

    NO_VALUE = "None"
    MINIO_SUCCESSFUL_MOUNT = "The minio bucket has been mounted"
    S3FS_NOT_FOUND = "s3fs not found. Install it with `sudo apt-get install s3fs`"
    HD2_NOT_FOUND = "HD2 not found"

    lock = threading.Lock()

    def __init__(self):
        self.config         = Config()
        self.meta_service   = Metadata_Service()
        self.status         = Status()
        self.storage        = Storage()

    def is_s3fs_installed(self):
        import apt
        cache = apt.Cache()
        return cache['s3fs'].is_installed

    def mount_minio_bucket_as_hd2(self, minio_url, user, access_token, bucket):
        retvalue = Minio_Sync.NO_VALUE
        while True:
            if not folder_exists(self.storage.hd2()):
                retvalue = Minio_Sync.HD2_NOT_FOUND
                break

            if not self.is_s3fs_installed():
                retvalue = Minio_Sync.S3FS_NOT_FOUND
                break

            passwd_s3fs = temp_file(extension="", contents=f"{user}:{access_token}")
            os.system(f"chmod 600 {passwd_s3fs}")
            print(f"s3fs {bucket} {self.storage.hd2()} -o passwd_file={passwd_s3fs},use_path_request_style,url={minio_url}")
            result = os.popen(f"s3fs {bucket} {self.storage.hd2()} -o passwd_file={passwd_s3fs},use_path_request_style,url={minio_url} -o nonempty").read()
            file_delete(passwd_s3fs)

            if result:
                retvalue = result
            else:
                retvalue = Minio_Sync.MINIO_SUCCESSFUL_MOUNT

            break

        return retvalue

    def umount_minio_hd2(self):
        os.system(f"umount -l {self.storage.hd2()}")
