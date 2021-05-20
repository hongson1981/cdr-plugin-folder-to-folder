import os
import requests
import zipfile
import shutil
import logging as logger
from datetime import datetime

from osbot_utils.utils.Files import folder_create, folder_delete_all, folder_copy, \
    path_combine, file_delete, file_exists, folder_exists, file_unzip
from osbot_utils.utils.Misc import random_text

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration

from cdr_plugin_folder_to_folder.pre_processing.Status import Status, FileStatus, Processing_Status

from cdr_plugin_folder_to_folder.processing.Analysis_Json import Analysis_Json
from cdr_plugin_folder_to_folder.processing.Events_Log import Events_Log
from cdr_plugin_folder_to_folder.metadata.Metadata import DEFAULT_REPORT_FILENAME
from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json
from cdr_plugin_folder_to_folder.utils.file_utils import FileService
logger.basicConfig(level=logger.INFO)

class Pre_Processor:

    def __init__(self):
        self.config         = Config()
        self.meta_service   = Metadata_Service()
        self.status         = Status()
        self.storage        = Storage()
        self.file_name      = None                              # set in process() method
        self.current_path   = None
        self.base_folder    = None
        self.dst_folder     = None
        self.dst_file_name  = None


    @log_duration
    def clear_data_and_status_folders(self):
        data_target      = self.storage.hd2_data()       # todo: refactor this clean up to the storage class
        status_target    = self.storage.hd2_status()
        processed_target = self.storage.hd2_processed()
        not_supported_target = self.storage.hd2_not_supported()
        folder_delete_all(data_target)
        folder_delete_all(status_target)
        folder_delete_all(processed_target)
        folder_delete_all(not_supported_target)
        folder_create(data_target)
        folder_create(status_target)
        folder_create(processed_target)
        folder_create(not_supported_target)
        self.status.reset()

    @log_duration
    def mark_all_hd2_files_unprocessed(self):

        if Processing_Status.NONE != self.status.get_current_status() and \
           Processing_Status.STOPPED != self.status.get_current_status():
            # do nothing if the processing has not been completed
            return

        for key in os.listdir(self.storage.hd2_not_supported()):
            source_path = self.storage.hd2_not_supported(key)
            destination_path = self.storage.hd2_data(key)
            if folder_exists(destination_path):
                folder_delete_all(destination_path)
            shutil.move(source_path, destination_path)

        for key in os.listdir(self.storage.hd2_processed()):
            source_path = self.storage.hd2_processed(key)
            destination_path = self.storage.hd2_data(key)
            if folder_exists(destination_path):
                folder_delete_all(destination_path)
            shutil.move(source_path, destination_path)

        self.status.reset_phase2()
        reset_data_folder_to_the_initial_state()

    def file_hash(self, file_path):
        return self.meta_service.file_hash(file_path)

    def prepare_folder(self, folder_to_process):
        abs_path_folder_to_process = os.path.abspath(folder_to_process)
        abs_path_hd1 = os.path.abspath(self.storage.hd1())

        if abs_path_folder_to_process.startswith(abs_path_hd1):
            return folder_to_process

        dirname = os.path.join(self.storage.hd1(), os.path.basename(folder_to_process))
        if os.path.isdir(dirname):
            folder_delete_all(dirname)
        try:
            folder_copy(folder_to_process, dirname)
        finally:
            return dirname

    def process_folder(self, folder_to_process):
        if not os.path.isdir(folder_to_process):
            # todo: add an event log
           return False

        folder_to_process = self.prepare_folder(folder_to_process)

        files_count = 0
        zip_info = {}
        for folderName, subfolders, filenames in os.walk(folder_to_process):
            for filename in filenames:
                file_path =  os.path.join(folderName, filename)
                if FileService.get_file_extension(filename) == ".zip":
                    unzipped_dir = self.pre_process_zip(file_path,filename)
                    if unzipped_dir:
                        zip_info[file_path] = unzipped_dir
                        for unzippedfolderName, unzippedsubfolders, unzippedfilenames in os.walk(unzipped_dir):
                            for unzippedfilename in unzippedfilenames:
                                unzipped_file_path = os.path.join(unzippedfolderName, unzippedfilename)
                                if os.path.isfile(unzipped_file_path):
                                    files_count += 1
                elif os.path.isfile(file_path):
                    files_count += 1

        self.status.set_files_count(files_count)

        for folderName, subfolders, filenames in os.walk(folder_to_process):
            for filename in filenames:
                file_path =  os.path.join(folderName, filename)
                if FileService.get_file_extension(filename) == ".zip":
                    self.pre_process_unzipped(zip_info[file_path])
                elif os.path.isfile(file_path):
                    self.process(file_path)

        return True

    @log_duration
    def pre_process_zip(self, file_path, filename):
        # Unzip to tmp
        randomdir = random_text()
        #unzip_path = '/tmp/' + randomdir
        unzip_path = '/'+os.path.splitext(filename)[0]+"_zip"
        try:
            if os.path.exists(unzip_path):
                folder_delete_all(unzip_path)
            os.mkdir(unzip_path)
            file_unzip(file_path, unzip_path)
            return unzip_path
        except Exception as e:
            print(str(e))
        return  None

    @log_duration
    def pre_process_unzipped(self, unzip_path):
        if unzip_path:
            for unzippedfolderName, unzippedsubfolders, unzippedfilenames in os.walk(unzip_path):
                for unzippedfilename in unzippedfilenames:
                    unzipped_file_path = os.path.join(unzippedfolderName, unzippedfilename)
                    if os.path.isfile(unzipped_file_path):
                        self.process(unzipped_file_path)

    @log_duration
    def process_files(self):
        self.status.StartStatusThread()
        self.status.set_phase_1()
        self.process_folder(self.storage.hd1())
        self.status.set_phase_2()
        self.status.StopStatusThread()

    @log_duration
    def process(self, file_path):
        tik  = datetime.now()

        metadata = self.meta_service.create_metadata(file_path=file_path)
        file_name      = metadata.get_file_name()
        original_hash  = metadata.get_original_hash()
        status         = metadata.get_rebuild_status()
        self.update_status(file_name, original_hash, status)

        tok   = datetime.now()
        delta = tok - tik

        if metadata.is_in_todo():
            hash_folder_path = self.storage.hd2_data(original_hash)
            self.meta_service.set_hd1_to_hd2_copy_time(hash_folder_path, delta.total_seconds())
        else:
            self.status.set_not_copied()

    def update_status(self, file_name, original_hash, status):
        if status == FileStatus.INITIAL:
            self.status.add_file()

    def process_downloaded_zip_file(self, url):
        retvalue = "No value"
        directory_name = url.replace('/', '_').replace(':', '').replace('.','_')
        zip_file_name = directory_name + '.zip'
        path_to_zip_file = path_combine(self.storage.hd1(), zip_file_name)
        path_to_extracted_folder = path_combine(self.storage.hd1(), directory_name)
        try:
            r = requests.get(url, allow_redirects=True)
            open(path_to_zip_file, 'wb').write(r.content)

            with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                zip_ref.extractall(path_to_extracted_folder)

            self.process_folder(path_to_extracted_folder)

            retvalue = f"The file from {url} has been processed"
        except Exception as e:
            retvalue = str(e)

        if file_exists(path_to_zip_file):
            file_delete(path_to_zip_file)

        return retvalue

def reset_data_folder_to_the_initial_state():

    storage = Storage()
    meta_service = Metadata_Service()

    hash_json_path = path_combine(storage.hd2_status(), Hash_Json.HASH_FILE_NAME)
    if file_exists(hash_json_path):
        file_delete(hash_json_path)

    events_json_path = path_combine(storage.hd2_status(), Events_Log.EVENTS_LOG_FILE_NAME)
    if file_exists(events_json_path):
        file_delete(events_json_path)

    for key in os.listdir(storage.hd2_data()):

        metadata_folder = storage.hd2_data(key)
        meta_service.reset_metadata(metadata_folder)

        # delete supplementary files in the metadata folder
        analysis_json_path = path_combine(metadata_folder, Analysis_Json.ANALYSIS_FILE_NAME)
        if file_exists(analysis_json_path):
            file_delete(analysis_json_path)

        events_json_path = path_combine(metadata_folder, Events_Log.EVENTS_LOG_FILE_NAME)
        if file_exists(events_json_path):
            file_delete(events_json_path)

        report_json_path = path_combine(metadata_folder, DEFAULT_REPORT_FILENAME)
        if file_exists(report_json_path):
            file_delete(report_json_path)

        errors_json_path = path_combine(metadata_folder, "error.json")
        if file_exists(errors_json_path):
            file_delete(errors_json_path)


    return True