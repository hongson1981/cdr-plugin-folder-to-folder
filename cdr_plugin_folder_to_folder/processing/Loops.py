import os
import os.path
import sys
import threading
import asyncio
import subprocess
import shutil
from multiprocessing.pool import ThreadPool

from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Files import create_folder, folder_exists, folder_delete_all

from cdr_plugin_folder_to_folder.common_settings.Config import Config, API_VERSION
from cdr_plugin_folder_to_folder.processing.Events_Log import Events_Log
from cdr_plugin_folder_to_folder.processing.Events_Log_Elastic import Events_Log_Elastic
from cdr_plugin_folder_to_folder.processing.File_Processing import File_Processing
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.pre_processing.Status import Status, FileStatus, Processing_Status
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import reset_data_folder_to_the_initial_state
from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json
from cdr_plugin_folder_to_folder.processing.Report_Elastic import Report_Elastic
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.processing.Endpoint_Service import Endpoint_Service

from elasticsearch import Elasticsearch
from datetime import datetime

from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.Logging import log_error, log_info
from cdr_plugin_folder_to_folder.processing.Analysis_Elastic import Analysis_Elastic

class Loops(object):

    continue_processing = False
    processing_started = False
    lock = asyncio.Lock()

    def __init__(self):
        self.use_es = False
        self.config = Config()
        self.status = Status()
        self.storage = Storage()
        self.hash_json = Hash_Json()
        self.events = Events_Log(self.config.hd2_status_location)
        self.events_elastic = Events_Log_Elastic()
        self.hash=None
        self.report_elastic = Report_Elastic()
        self.analysis_elastic = Analysis_Elastic()
        self.endpoint_service = Endpoint_Service()
        self.report_elastic.setup()
        self.analysis_elastic.setup()
        create_folder(self.storage.hd2_processed())
        create_folder(self.storage.hd2_not_supported())


    def IsProcessing(self):
        return Loops.processing_started

    def StopProcessing(self):
        Loops.continue_processing = False
        self.status.set_stopping()

    def HasBeenStopped(self):
        return not Loops.continue_processing

    def git_commit(self):
        git_commit = 'Not available'
        try:
            git_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode("utf-8").rstrip()
        except Exception as e:
            pass

        return git_commit

    def ProcessDirectoryWithEndpoint(self, itempath, file_hash, endpoint_index,):

        if not os.path.isdir(itempath):
            return False

        log_info(message=f"Starting ProcessDirectoryWithEndpoint on endpoint # {endpoint_index} for file {file_hash}")
        meta_service = Metadata_Service()
        original_file_path = meta_service.get_original_file_paths(itempath)
        events = Events_Log(itempath)

        meta_service.set_f2f_plugin_version(itempath, API_VERSION)
        meta_service.set_f2f_plugin_git_commit(itempath, self.git_commit())

        endpoint = self.endpoint_service.get_endpoint_url()
        if not endpoint:
            meta_service.set_status(itempath, FileStatus.FAILED)
            meta_service.set_error(itempath, "No valid endpoints while processing the file")
            return False

        events.add_log("Processing with: " + endpoint)

        try:
            file_processing = File_Processing(events, self.events_elastic, self.report_elastic, self.analysis_elastic, meta_service)
            if not file_processing.processDirectory(endpoint, itempath, self.config.use_rebuild_zip):
                events.add_log("CANNOT be processed")
                return False

            log_data = {
                    'file': original_file_path,
                    'status': FileStatus.COMPLETED,
                    'error': 'none',
                    'timestamp': datetime.now(),
                }
            log_info('ProcessDirectoryWithEndpoint', data=log_data)
            events.add_log("Has been processed")
            return True
        except Exception as error:
            log_data = {
                'file': original_file_path,
                'status': FileStatus.FAILED,
                'error': str(error),
            }
            log_error(message='error in ProcessDirectoryWithEndpoint', data=log_data)
            meta_service.set_error(itempath, str(error))
            meta_service.set_status(itempath, FileStatus.FAILED)
            self.hash_json.update_status(file_hash, FileStatus.FAILED)
            events.add_log("ERROR:" + str(error))
            return False


    def ProcessDirectory(self, thread_data):
        (itempath, file_hash, process_index) = thread_data
        endpoint_index = process_index % self.config.endpoints_count
        if not Loops.continue_processing:
            return False
        tik = datetime.now()
        process_result = self.ProcessDirectoryWithEndpoint(itempath, file_hash, endpoint_index)
        tok = datetime.now()

        delta = tok - tik
        meta_service = Metadata_Service()
        meta_service.set_hd2_to_hd3_copy_time(itempath, delta.total_seconds())

        if not process_result:
            self.status.add_failed()

        return process_result

        # note: removing retries from this method (it should not be handled like this
        #for idx in range(self.config.endpoints_count):
        #    if self.ProcessDirectoryWithEndpoint(itempath, file_hash, endpoint_index):
        #        return
        #    # The Endpoint failed to process the file
        #    # Retry it with the next one
        #    endpoint_index = (endpoint_index + 1) % self.config.endpoints_count

    def updateHashJson(self):
        self.hash_json.reset()
        meta_service = Metadata_Service()

        for hash_folder in os.listdir(self.storage.hd2_data()):

            metadata_folder = self.storage.hd2_data(hash_folder)

            if not os.path.isdir(metadata_folder):
                continue

            metadata       = meta_service.get_from_file(metadata_folder)
            file_name      = metadata.get_file_name()
            original_hash  = metadata.get_original_hash()
            status         = metadata.get_rebuild_status()

            if status != FileStatus.COMPLETED:
                self.hash_json.add_file(original_hash, file_name)

        self.hash_json.save()

        if Processing_Status.PHASE_2 != self.status.get_current_status():
            self.status.reset_phase2()
            reset_data_folder_to_the_initial_state()

        return self.hash_json.data()

    def moveProcessedFiles(self):
        json_list = self.hash_json.data()

        for key in json_list:

            source_path = self.storage.hd2_data(key)
            destination_path = ""

            file_status = json_list[key]["file_status"]

            if (FileStatus.COMPLETED == file_status) or \
               (FileStatus.NO_CLEANING_NEEDED == file_status):
                destination_path = self.storage.hd2_processed(key)
            elif (FileStatus.NOT_SUPPORTED == file_status):
                destination_path = self.storage.hd2_not_supported(key)
            else:
                continue

            if destination_path:
                if folder_exists(destination_path):
                    folder_delete_all(destination_path)
                shutil.move(source_path, destination_path)

    def LoopHashDirectoriesInternal(self, thread_count, do_single):

        self.endpoint_service.get_endpoints()

        if folder_exists(self.storage.hd2_data()) is False:
            log_message = "ERROR: rootdir does not exist: " + self.storage.hd2_data()
            log_error(log_message)
            return False

        if not isinstance(thread_count,int):
            raise TypeError("thread_count must be a integer")

        if not isinstance(do_single,bool):
            raise TypeError("thread_count must be a integer")

        log_message = f"LoopHashDirectoriesInternal started with {thread_count} threads"
        self.events.add_log(log_message)
        log_info(log_message)

        json_list = self.updateHashJson()

        log_message = f"LoopHashDirectoriesInternal started with {thread_count} threads"
        self.events.add_log(log_message)
        log_info(log_message)

        threads = list()

        process_index   = 0

        log_info(message=f'before Mapping thread_data for {len(json_list)} files')
        thread_data = []

        self.endpoint_service.StartServiceThread()

        for key in json_list:
            file_hash   =  key

            itempath = self.storage.hd2_data(key)
            if (FileStatus.COMPLETED == json_list[key]["file_status"]):
                self.events.add_log(f"The file processing has been already completed")
                continue

            if not os.path.exists(itempath):
                self.events.add_log(f"ERROR: Path \"{itempath}\" does not exist")
                json_list[key]["file_status"] = FileStatus.FAILED
                continue

            process_index += 1
            thread_data.append((itempath, file_hash, process_index, ))
            # # limit the number of parallel threads
            #
            # if process_index % int(thread_count) == 0:                      # todo: refactor this workflow to use multiprocess and queues
            #     # Clean up the threads
            #     for index, thread in enumerate(threads):                    # todo: since at the moment this will block allocating new threads until
            #         thread.join()                                           #       all have finishing execution
            #
            # process_index += 1
            # log_info(message=f"in LoopHashDirectoriesInternal process_index={process_index} , thread #{process_index % int(thread_count) }")
            # x = threading.Thread(target=self.ProcessDirectory, args=(itempath, file_hash, process_index,))
            # threads.append(x)
            # x.start()
            #
            # if do_single:
            #     break
            #
            # if not Loops.continue_processing:
            #     break

        # for index, thread in enumerate(threads):
        #     thread.join()

        log_info(message=f'after mapped thread_data, there are {len(thread_data)} mapped items')
        #thread_data = thread_data[:500]
        #log_info(message=f'to start with only processing {len(thread_data)} thread_data items')
        pool = ThreadPool(thread_count)
        results = pool.map(self.ProcessDirectory, thread_data)
        pool.close()
        pool.join()

        self.moveProcessedFiles()

        self.endpoint_service.StopServiceThread()

        self.events.add_log("LoopHashDirectoriesInternal finished")
        return True

    async def LoopHashDirectoriesAsync(self, thread_count, do_single = False):
        await Loops.lock.acquire()
        try:
            Loops.continue_processing = True
            Loops.processing_started = True
            self.status.set_started()
            self.LoopHashDirectoriesInternal(thread_count, do_single)
        finally:
            Loops.processing_started = False
            Loops.lock.release()
            self.status.set_stopped()
            self.hash_json.save()

    @log_duration
    def LoopHashDirectories(self, thread_count=None):
        #Allow only a single loop to be run at a time
        if self.IsProcessing():
            log_error(message="ERROR: Attempt to start processing while processing is in progress")
            return False

        self.status.StartStatusThread()
        thread_count = thread_count or self.config.thread_count
        log_info(message="in LoopHashDirectories, about to start main loop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.LoopHashDirectoriesAsync(thread_count))
        log_info(message="in LoopHashDirectories, Loop completed")
        self.status.StopStatusThread()
        return True

    @log_duration
    def LoopHashDirectoriesSequential(self):
        #Allow only a single loop to be run at a time
        if self.IsProcessing():
            log_error("ERROR: Attempt to start processing while processing is in progress")
            return False

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.LoopHashDirectoriesAsync(1))
        return True

    @log_duration
    def ProcessSingleFile(self):
        if self.IsProcessing():
            log_error("ERROR: Attempt to start processing while processing is in progress")
            return False

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.LoopHashDirectoriesAsync(1, True))
        return True
