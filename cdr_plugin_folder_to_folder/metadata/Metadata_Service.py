import hashlib
import json
import os

import logging as logger

from osbot_utils.utils.Files import file_sha256
from osbot_utils.utils.Json import json_save_file_pretty
from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.metadata.Metadata import Metadata
from cdr_plugin_folder_to_folder.pre_processing.Status import FileStatus

from enum import Enum

from cdr_plugin_folder_to_folder.metadata.Metadata_Elastic import Metadata_Elastic
from cdr_plugin_folder_to_folder.utils.Logging import log_info

logger.basicConfig(level=logger.INFO)

class Metadata_Service:

    METADATA_FILE_NAME = "metadata.json"

    def __init__(self):
        self.file_path        = None
        self.metadata_folder  = None
        self.metadata         = None
        self.config           = Config()
        self.metadata_elastic = Metadata_Elastic().setup()

    def create_metadata(self, file_path):
        self.metadata = Metadata()
        self.metadata.add_file(file_path)

        self.metadata_elastic.add_metadata(self.metadata.data)                            # save metadata to elastic
        log_info(message=f"created metadata for: {self.metadata.get_file_name()}", data={"file_path": file_path, "metadata_file_path": self.metadata.metadata_file_path()})
        return self.metadata

    def get_from_file(self, metadata_folder):
        self.metadata = Metadata(os.path.basename(metadata_folder))
        self.metadata.get_from_file()
        self.metadata_folder=metadata_folder
        return self.metadata

    def get_metadata_file_path(self):
        return os.path.join(self.metadata_folder, Metadata_Service.METADATA_FILE_NAME)

    def file_hash(self, file_path):
        return file_sha256(file_path)

    def get_original_file_paths(self, metadata_folder):
        self.get_from_file(metadata_folder)
        return self.metadata.get_original_file_paths()

    def get_status(self, metadata_folder):
        self.get_from_file(metadata_folder)
        return self.metadata.get_rebuild_status()

    def is_completed_status(self, metadata_folder):
        return (self.get_status(metadata_folder) == FileStatus.COMPLETED)

    def set_status_inprogress(self, metadata_folder):
        self.set_status(metadata_folder, FileStatus.IN_PROGRESS)

    def set_metadata_field(self, metadata_folder, field_name, value):
        self.get_from_file(metadata_folder)
        self.metadata.update_field(field_name, value)
        self.metadata_elastic.add_metadata(self.metadata.data) # save metadata to elastic

    def set_status(self, metadata_folder, rebuild_status):
        self.set_metadata_field(metadata_folder, 'rebuild_status', rebuild_status)

    def set_error(self, metadata_folder, error_details):
        self.set_metadata_field(metadata_folder, 'error', error_details)

    def set_xml_report_status(self, metadata_folder, xml_report_status):
        self.set_metadata_field(metadata_folder, 'xml_report_status', xml_report_status)

    def set_response_code(self, metadata_folder, response_code):
        self.set_metadata_field(metadata_folder, 'response_code', response_code)

    def set_rebuild_server(self, metadata_folder, rebuild_server):
        self.set_metadata_field(metadata_folder, 'rebuild_server', rebuild_server)

    def set_server_version(self, metadata_folder, server_version):
        self.set_metadata_field(metadata_folder, 'server_version', server_version)

    def set_sdk_api_version(self, metadata_folder, sdk_api_version):
        self.set_metadata_field(metadata_folder, 'sdk_api_version', sdk_api_version)

    def set_sdk_engine_version(self, metadata_folder, skd_engine_version):
        self.set_metadata_field(metadata_folder, 'skd_engine_version', skd_engine_version)

    def set_adaptation_file_id(self, metadata_folder, adaptation_file_id):
        self.set_metadata_field(metadata_folder, 'adaptation_file_id', adaptation_file_id)

    def set_rebuild_file_path(self, metadata_folder, rebuild_file_path):
        self.set_metadata_field(metadata_folder, 'rebuild_file_path', rebuild_file_path)

    def set_rebuild_hash(self, metadata_folder, rebuild_hash):
        self.set_metadata_field(metadata_folder, 'rebuild_hash', rebuild_hash)

    def set_rebuild_file_size(self, metadata_folder, file_size):
        self.set_metadata_field(metadata_folder, 'rebuild_file_size', file_size)

    def set_rebuild_file_extension(self, metadata_folder, file_extension):
        self.set_metadata_field(metadata_folder, 'rebuild_file_extension', file_extension)

    def set_rebuild_file_duration(self, metadata_folder, rebuild_file_duration):
        self.set_metadata_field(metadata_folder, 'rebuild_file_duration', rebuild_file_duration)

    def set_f2f_plugin_version(self, metadata_folder, rebuild_file_duration):
        self.set_metadata_field(metadata_folder, 'f2f_plugin_version', rebuild_file_duration)

    def set_f2f_plugin_git_commit(self, metadata_folder, rebuild_file_duration):
        self.set_metadata_field(metadata_folder, 'f2f_plugin_git_commit', rebuild_file_duration)

    def set_hd1_to_hd2_copy_time(self,metadata_folder, seconds):
        self.set_metadata_field(metadata_folder, 'hd1_to_hd2_copy_time', seconds)

    def set_hd2_to_hd3_copy_time(self,metadata_folder, seconds):
        self.set_metadata_field(metadata_folder, 'hd2_to_hd3_copy_time', seconds)

    def reset_metadata(self, metadata_folder):
        self.set_xml_report_status(metadata_folder, None)
        self.set_response_code(metadata_folder, None)
        self.set_rebuild_server(metadata_folder, None)
        self.set_server_version(metadata_folder, None)
        self.set_sdk_api_version(metadata_folder, None)
        self.set_skd_engine_version(metadata_folder, None)
        self.set_adaptation_file_id(metadata_folder, None)
        self.set_error(metadata_folder, None)
        self.set_rebuild_file_path(metadata_folder, None)
        self.set_rebuild_hash(metadata_folder, None)
        self.set_status(metadata_folder, FileStatus.INITIAL)
        self.set_rebuild_file_extension(metadata_folder, None)
        self.set_rebuild_file_size(metadata_folder, None)
        self.set_rebuild_file_duration(metadata_folder, None)
        self.set_f2f_plugin_version(metadata_folder, None)
        self.set_f2f_plugin_git_commit(metadata_folder, None)
        self.set_hd1_to_hd2_copy_time(metadata_folder, None)
        self.set_hd2_to_hd3_copy_time(metadata_folder, None)

