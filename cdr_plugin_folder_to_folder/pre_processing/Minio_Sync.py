import os
import subprocess
import validators
import logging as logger
from datetime import datetime

from osbot_utils.utils.Files import file_delete, file_exists, folder_exists, temp_file

from cdr_plugin_folder_to_folder.common_settings.Config import Config, DEFAULT_THREAD_COUNT
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration

from cdr_plugin_folder_to_folder.pre_processing.Processing_Status import Processing_Status
from cdr_plugin_folder_to_folder.pre_processing.Status import Status, FileStatus

import threading
from multiprocessing.pool import ThreadPool

import importlib.util
import sys

logger.basicConfig(level=logger.INFO)

class Minio_Sync:

    NO_VALUE = "None"
    MINIO_SUCCESSFUL_MOUNT = "The minio bucket has been mounted"
    MINIO_UMOUNT = "The minio bucket has been unmounted"
    NO_BUCKET_MOUNTED = "No bucket is currently mounted"
    S3FS_NOT_FOUND = "s3fs not found. Install it with `sudo apt-get install s3fs`"
    HD2_NOT_FOUND = "The mount point for HD2 not found"
    INVALID_PARAMETERS = "Invalid parameters"
    INVALID_MINIO_URL = "Invalid Minio URL provided"

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
        if not folder_exists(self.storage.hd2()):
            return Minio_Sync.HD2_NOT_FOUND

        if not user or not access_token or not bucket:
            return Minio_Sync.INVALID_PARAMETERS

        if not validators.url(minio_url):
            return Minio_Sync.INVALID_MINIO_URL

        # if not self.is_s3fs_installed():
        #     return Minio_Sync.S3FS_NOT_FOUND

        hd2_mount_path = self.status.get_hd2_mount_path()
        hd2_remote_path = self.status.get_hd2_remote_bucket()
        if hd2_mount_path:
            return f"Currently {hd2_remote_path} is mounted at {hd2_mount_path}."

        passwd_s3fs = temp_file(extension="", contents=f"{user}:{access_token}")
        os.system(f"chmod 600 {passwd_s3fs}")
        s3fs_command = f"s3fs {bucket} {self.storage.hd2()} -o passwd_file={passwd_s3fs},use_path_request_style,url={minio_url},nonempty"
        result = subprocess.run(["s3fs", f"{bucket}", f"{self.storage.hd2()}", "-o", f"passwd_file={passwd_s3fs},use_path_request_style,url={minio_url},nonempty"], stdout=subprocess.PIPE)
        result_str = result.stdout.decode('utf-8')
        file_delete(passwd_s3fs)

        self.status.update_hd2_mount_data(self.storage.hd2(),f"{minio_url}/{bucket}")


        if result_str:
            return result_str
        else:
            return Minio_Sync.MINIO_SUCCESSFUL_MOUNT


    def umount_minio_hd2(self):
        hd2_mount_path = self.status.get_hd2_mount_path()
        #hd2_remote_path = self.status.get_hd2_remote_bucket()

        if not hd2_mount_path:
            return Minio_Sync.NO_BUCKET_MOUNTED

        os.system(f"umount -l {hd2_mount_path}")
        self.status.update_hd2_mount_data()
        return Minio_Sync.MINIO_UMOUNT
