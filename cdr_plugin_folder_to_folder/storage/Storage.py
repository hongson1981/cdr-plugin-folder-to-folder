import os
from os import listdir
from os.path import abspath

from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.utils.Files import temp_folder, path_combine, file_exists, file_copy, folder_delete_all, folder_create

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils import file_utils
from cdr_plugin_folder_to_folder.utils.file_utils import FileService


class Storage:
    def __init__(self):
        self.config    = Config()
        #self.path_hd1  = None
        #self.path_hd2  = None
        #self.path_hd3  = None
        #self.path_root = None

    def hd1(self, path=''):                                     # todo: rename to hd1 path
        return path_combine(self.config.hd1_location, path)

    def hd1_add_file(self, path):       # todo add support for child folders
        if file_exists(path):
            return file_copy(path, self.hd1())

    def hd1_delete_all_files(self):
        folder_delete_all(self.hd1())
        folder_create(self.hd1())

    def hd1_files(self):
        return FileService.files_in_folder(self.hd1())

    def hd1_file_path(self, file_path_in_hd1):
        full_path = path_combine(self.hd1(), file_path_in_hd1)
        if full_path.startswith(self.hd1()) and file_exists(full_path):
            return full_path

    def hd2(self):
        return abspath(self.config.hd2_location                   )   # convert to absolute paths

    def hd2_data(self, path=''):
        return path_combine(self.config.hd2_data_location, path   )   # add path and convert to absolute paths

    def hd2_processed(self, path=''):
        return path_combine(self.config.hd2_processed_location, path   )   # add path and convert to absolute paths

    def hd2_not_processed(self, path=''):
        return path_combine(self.config.hd2_not_processed_location, path   )   # add path and convert to absolute paths

    def hd2_delete_all_files(self):
        folder_delete_all(self.hd2_data())
        folder_delete_all(self.hd2_status())
        folder_create(self.hd2_data())
        folder_create(self.hd2_status())

    def hd2_file_hashes(self):
        hashes = []
        for folder in os.listdir(self.hd2_data()):
            hashes.append(folder)
        return hashes

    @index_by
    @group_by
    def hd2_metadatas(self):
        from cdr_plugin_folder_to_folder.metadata.Metadata import Metadata
        metadatas = []
        for file_hash in self.hd2_file_hashes():
            metadata = Metadata(file_hash=file_hash).load()
            if metadata.exists():
                metadatas.append(metadata.data)
        return metadatas

    def hd2_processed(self, path=''):
        return path_combine(self.config.hd2_processed_location, path )

    def hd2_status(self, path=''):
        return path_combine(self.config.hd2_status_location, path )  # add path and convert to absolute paths

    def hd3(self, path=''):
        return path_combine(self.config.hd3_location, path        )  # add path and convert to absolute paths

    def hd3_files(self):
        return FileService.files_in_folder(self.hd3())




