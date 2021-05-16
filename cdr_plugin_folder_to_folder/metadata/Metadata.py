import os
import json
import pathlib
from datetime import datetime

from osbot_utils.utils.Files import file_name, folder_exists, file_sha256, file_exists, folder_create, path_combine, \
    folder_delete_all, file_copy, files_list
from osbot_utils.utils.Json import json_save_file_pretty
from osbot_utils.utils.Misc import datetime_now

from cdr_plugin_folder_to_folder.metadata.Metadata_Utils import Metadata_Utils
from cdr_plugin_folder_to_folder.pre_processing.Status import Status, FileStatus
from cdr_plugin_folder_to_folder.processing.Events_Log import Events_Log
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.common_settings.Config import Config

DEFAULT_REPORT_FILENAME   = "report.json"
DEFAULT_METADATA_FILENAME = "metadata.json"
DEFAULT_SOURCE_FILENAME   = "source"

class Metadata:

    def __init__(self, file_hash=None):
        self.config         = Config()
        self.storage        = Storage()
        self.process_status = Status()
        self.metadata_utils = Metadata_Utils()
        self.path_hd1       = self.storage.hd1()
        self.data           = self.default_data()
        self.file_hash      = file_hash
        #self.time_field    =

    def get_from_file(self):                # todo: refactor out this method
        self.load()
        return self.data

    def load(self):
        with open(self.metadata_file_path()) as json_file:
            self.data = json.load(json_file)
        return self

    def add_file(self, file_path):
        if file_exists(file_path):
            tik = datetime.now()

            self.set_file_hash(self.metadata_utils.file_hash(file_path))

            tok = datetime.now()
            delta = tok - tik
            self.set_file_hash_calculation_time(delta.total_seconds())

            if self.exists():
                self.get_from_file()
            else:
                self.create(file_path)
            self.add_file_path(file_path)
            self.save()
            return self.file_hash

    def add_file_path(self, file_path:str):
        if self.file_hash:
            file_paths = self.data.get('original_file_paths')
            if 0 == len(file_paths):
                self.process_status.add_to_be_processed()
            if file_path.startswith(self.path_hd1):                         # check if path starts with hd1
                file_path = os.path.relpath(file_path, self.path_hd1)
            if file_path not in file_paths:
                file_paths.append(file_path)
            return file_paths

    def create(self, file_path):
        if self.file_hash:
            folder_create(self.metadata_folder_path())
            file_copy    (file_path, self.source_file_path())
            self.set_original_file_size     (file_path)
            self.set_original_file_extension(file_path)
            self.set_original_file_name     (file_path)

    def default_data(self):
        return {   'file_name'              : None               ,
                   'xml_report_status'      : None               ,
                   'last_update_time'       : None               ,
                   'rebuild_server'         : None               ,
                   'server_version'         : None               ,
                   'error'                  : None               ,
                   'original_file_paths'    : []                 ,
                   'original_hash'          : None               ,
                   'original_hash_calculation_time': None        ,
                   'original_file_extension': None               ,
                   'original_file_size'     : None               ,
                   'rebuild_file_path'      : None               ,
                   'rebuild_hash'           : None               ,
                   'rebuild_status'         : FileStatus.INITIAL ,
                   'rebuild_file_extension' : None               ,
                   'rebuild_file_size'      : None               ,
                   'rebuild_file_duration'  : None               ,
                   'f2f_plugin_version'     : None               ,
                   'f2f_plugin_git_commit'  : None               ,
                   'hd1_to_hd2_copy_time'   : None               ,
                   'hd2_to_hd3_copy_time'   : None
                 }

    def delete(self):
        if self.exists():
            folder_delete_all(self.metadata_folder_path())
            return self.exists() is False
        return False

    def exists(self):
        return folder_exists(self.metadata_folder_path())

    def events_log(self):
        return Events_Log(self.metadata_folder_path())

    def metadata_file_exists(self):
        return file_exists(self.metadata_file_path())

    def metadata_file_path(self):
        if self.file_hash:                              # todo: find a better solution that having to add this to all methods
            return path_combine(self.metadata_folder_path(), DEFAULT_METADATA_FILENAME)

    def metadata_folder_path(self):
        if not self.file_hash:
            return

        path = self.storage.hd2_not_supported(self.file_hash)
        if folder_exists(path):
            return path

        path = self.storage.hd2_processed(self.file_hash)
        if folder_exists(path):
            return path

        # never processed - must be in the 'todo' folder
        path = self.storage.hd2_data(self.file_hash)
        return path

    def is_in_todo(self):
        folder_exists(self.storage.hd2_data(self.file_hash))

    def is_in_processed(self):
        folder_exists(self.storage.hd2_processed(self.file_hash))

    def is_in_not_supported(self):
        folder_exists(self.storage.hd2_not_supported(self.file_hash))

    def save(self):
        if self.exists():
            json_save_file_pretty(python_object=self.data, path=self.metadata_file_path())

    def update_field(self, field, updated_value):                       # todo: optimise this if we get performance hits due to multiple updates
        self.data[field] = updated_value
        self.data['last_update_time'] = datetime_now()
        self.save()

    def set_file_hash(self, file_hash):
        self.file_hash = file_hash
        self.data['original_hash'] = file_hash
        self.data['last_update_time'] = datetime_now()
        if not self.exists():
            self.save()

    def set_file_hash_calculation_time(self,seconds):
        self.data['original_hash_calculation_time'] = seconds

    def set_original_file_name(self, file_path):
        original_file_name = file_name(file_path)
        self.update_field('file_name', original_file_name)

    def set_original_file_size(self, file_path):
        file_size = os.path.getsize(file_path)
        self.update_field('original_file_size', file_size)

    def set_original_file_extension(self, file_path):
        extension = pathlib.Path(file_path).suffix
        self.update_field('original_file_extension', extension)

    def source_file_path(self):
        if self.file_hash:
            return path_combine(self.metadata_folder_path(), DEFAULT_SOURCE_FILENAME)

    def get_original_hash(self):
        return self.data.get('original_hash')

    def get_file_hash(self):
        return self.file_hash

    def get_file_name(self):
        return self.data.get('file_name')

    def get_rebuild_status(self):
        return self.data.get('rebuild_status')

    def get_original_file_paths(self):
        return self.data.get('original_file_paths')

    def get_last_update_time(self):
        return self.data.get('last_update_time')

    def get_error(self):
        return self.data.get('error')

    def get_original_file_extension(self):
        return self.data.get('original_file_extension')

    def report_file_path(self):
        if self.file_hash:
            return path_combine(self.metadata_folder_path(), DEFAULT_REPORT_FILENAME)

    def report_file_exists(self):
        return file_exists(self.report_file_path())
