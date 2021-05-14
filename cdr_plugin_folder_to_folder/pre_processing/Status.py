import os
import threading
import psutil
import logging as logger
from time import sleep

from osbot_utils.utils.Files                        import path_combine, folder_create, file_create
from osbot_utils.utils.Json                         import json_save_file_pretty, json_load_file, file_exists
from cdr_plugin_folder_to_folder.storage.Storage    import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration

logger.basicConfig(level=logger.INFO)

class FileStatus:                                     # todo move to separate file (either per enum or with all enums)
    INITIAL       = "Initial"
    NOT_COPIED    = "Will not be copied"
    IN_PROGRESS   = "In Progress"
    COMPLETED     = "Completed Successfully"
    NOT_SUPPORTED = "The file type in not currently supported"
    FAILED        = "Completed with errors"
    TO_PROCESS    = "To Process"
    NONE          = "None"


class Processing_Status:
    NONE     = "None"
    STOPPED  = "Stopped"
    STOPPING = "Stopping"
    STARTED  = "Started"
    PHASE_1  = "PHASE 1 - Copying Files"
    PHASE_2  = "PHASE 2 - Rebuilding Files"

class Status:

    STATUS_FILE_NAME             = "status.json"
    VAR_COMPLETED                = "completed"
    VAR_CURRENT_STATUS           = "current_status"
    VAR_NOT_SUPPORTED            = "not_supported"
    VAR_FAILED                   = "failed"
    VAR_FILES_TO_PROCESS         = "files_to_process"
    VAR_FILES_LEFT_TO_PROCESS    = "files_left_to_process"
    VAR_FILES_COUNT              = "files_in_hd1_folder"
    VAR_FILES_COPIED             = "files_copied"
    VAR_FILES_TO_BE_COPIED       = "files_left_to_be_copied"
    VAR_IN_PROGRESS              = "in_progress"
    VAR_NUMBER_OF_CPUS           = "number_of_cpus"
    VAR_CPU_UTILIZATION          = "cpu_utilization"
    VAR_RAM_UTILIZATION          = "memory_utilization"
    VAR_NUM_OF_PROCESSES         = "number_of_processes"
    VAR_NUM_OF_THREADS           = "number_of_threads"
    VAR_NETWORK_CONNECTIONS      = "network_connections"
    VAR_DISK_PARTITIONS          = "disk_partitions"

    lock = threading.Lock()

    _instance = None
    def __new__(cls):                                               # singleton pattern
        if cls._instance is None:
            cls._instance = super(Status, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'instantiated') is False:                     # only set these values first time around
            self.instantiated   = True
            self.storage        = Storage()
            #self._on_save      = []                             # todo: add support for firing up events when data is saved
            self._status_data   = self.default_data()
            self.status_thread_on = False
            self.status_thread = threading.Thread()

    @classmethod
    def clear_instance(cls):
        del cls.instance

    def StatusThread(self, update_interval):
        while self.status_thread_on:
            self.get_server_status()
            sleep(update_interval)

    def StartStatusThread(self):
        if self.status_thread_on:
            return

        self.status_thread_on = True
        self.status_thread = threading.Thread(target=self.StatusThread, args=(1,))
        self.status_thread.start()

    def StopStatusThread(self):
        self.status_thread_on = False
        self.status_thread.join()

    def data(self):
        return self._status_data

    def default_data(self):
        return {    Status.VAR_CURRENT_STATUS         : FileStatus.NONE ,
                    Status.VAR_FILES_COUNT            : 0               ,
                    Status.VAR_FILES_COPIED           : 0               ,
                    Status.VAR_FILES_TO_BE_COPIED     : 0               ,
                    Status.VAR_FILES_TO_PROCESS       : 0               ,
                    Status.VAR_FILES_LEFT_TO_PROCESS  : 0               ,
                    Status.VAR_COMPLETED              : 0               ,
                    Status.VAR_NOT_SUPPORTED          : 0               ,
                    Status.VAR_FAILED                 : 0               ,
                    Status.VAR_IN_PROGRESS            : 0               ,
                    Status.VAR_NUMBER_OF_CPUS         : psutil.cpu_count()            ,
                    Status.VAR_CPU_UTILIZATION        : None            ,
                    Status.VAR_RAM_UTILIZATION        : None            ,
                    Status.VAR_NUM_OF_PROCESSES       : None            ,
                    Status.VAR_NUM_OF_THREADS         : None            ,
                    Status.VAR_NETWORK_CONNECTIONS    : None            ,
                    Status.VAR_DISK_PARTITIONS        : len(psutil.disk_partitions())  ,
                }

    def load_data(self):
        self._status_data = json_load_file(self.status_file_path())
        if self.data() == {}:
            self.reset()
        return self


    def reset(self):
        self._status_data = self.default_data()
        self.save()
        return self

    def save(self):
        if not file_exists(self.status_file_path()):
            folder_create(  self.storage.hd2_status() )
            file_create  (  self.status_file_path()   )

        json_save_file_pretty(self.data(), self.status_file_path())
        return self

    def status_file_path(self):
        return path_combine(self.storage.hd2_status(), Status.STATUS_FILE_NAME)

    def get_server_data(self):
        self._status_data[Status.VAR_NUMBER_OF_CPUS] = psutil.cpu_count()

        self._status_data[Status.VAR_CPU_UTILIZATION] = psutil.cpu_percent(interval=1, percpu=True)
        self._status_data[Status.VAR_RAM_UTILIZATION] = psutil.virtual_memory().percent

        pids = psutil.pids()
        self._status_data[Status.VAR_NUM_OF_PROCESSES] = len(pids)

        thread_count = 0
        for pid in pids:
            try:
                p = psutil.Process(int(pid))
                process_treads = p.num_threads()
                thread_count += process_treads
            except:
                pass

        self._status_data[Status.VAR_NUM_OF_THREADS] = thread_count

        self._status_data[Status.VAR_NETWORK_CONNECTIONS] = len(psutil.net_connections(kind='tcp'))

        self._status_data[Status.VAR_DISK_PARTITIONS] = len(psutil.disk_partitions())


    def get_server_status(self):
        Status.lock.acquire()
        try:
            self.get_server_data()
        finally:
            Status.lock.release()
            self.save()

        return self

    def set_processing_status(self, processing_status):
        Status.lock.acquire()
        try:
            data = self.data()
            data[Status.VAR_CURRENT_STATUS] = processing_status
        finally:
            Status.lock.release()
            self.save()

        return self

    def set_started      (self       ): return self.set_processing_status(Processing_Status.STARTED  )
    def set_stopping     (self       ): return self.set_processing_status(Processing_Status.STOPPING )
    def set_stopped      (self       ): return self.set_processing_status(Processing_Status.STOPPED  )
    def set_phase_1      (self       ): return self.set_processing_status(Processing_Status.PHASE_1  )
    def set_phase_2      (self       ): return self.set_processing_status(Processing_Status.PHASE_2  )

    def update_counters(self, updated_status, count=0):
        Status.lock.acquire()
        try:
            data = self.data()

            if updated_status == FileStatus.NONE:
                data[Status.VAR_FILES_COUNT] = count
                data[Status.VAR_FILES_TO_BE_COPIED] = count
                
            elif updated_status == FileStatus.INITIAL:
                data[Status.VAR_FILES_COPIED] += 1
                if data[Status.VAR_FILES_TO_BE_COPIED] > 0:
                    data[Status.VAR_FILES_TO_BE_COPIED] -= 1

            elif updated_status == FileStatus.NOT_COPIED:
                if data[Status.VAR_FILES_TO_BE_COPIED] > 0:
                    data[Status.VAR_FILES_TO_BE_COPIED] -= 1

            elif updated_status == FileStatus.IN_PROGRESS:
                data[Status.VAR_IN_PROGRESS] += 1

            elif updated_status == FileStatus.COMPLETED:
                data[Status.VAR_COMPLETED] += 1
                if data[Status.VAR_IN_PROGRESS] > 0:
                    data[Status.VAR_IN_PROGRESS] -= 1
                if data[Status.VAR_FILES_LEFT_TO_PROCESS] > 0:
                    data[Status.VAR_FILES_LEFT_TO_PROCESS] -= 1

            elif updated_status == FileStatus.NOT_SUPPORTED:
                data[Status.VAR_NOT_SUPPORTED] += 1
                if data[Status.VAR_IN_PROGRESS] > 0:
                    data[Status.VAR_IN_PROGRESS] -= 1
                if data[Status.VAR_FILES_LEFT_TO_PROCESS] > 0:
                    data[Status.VAR_FILES_LEFT_TO_PROCESS] -= 1

            elif updated_status == FileStatus.FAILED:
                data[Status.VAR_FAILED] += 1
                if data[Status.VAR_IN_PROGRESS] > 0:
                    data[Status.VAR_IN_PROGRESS] -= 1
                if data[Status.VAR_FILES_LEFT_TO_PROCESS] > 0:
                    data[Status.VAR_FILES_LEFT_TO_PROCESS] -= 1

            elif updated_status == FileStatus.TO_PROCESS:
                data[Status.VAR_FILES_TO_PROCESS] += 1
                data[Status.VAR_FILES_LEFT_TO_PROCESS] += 1

        finally:
            Status.lock.release()
            self.save()

        return self

    def reset_phase2(self):

        Status.lock.acquire()
        try:
            self.reset()
            data = self.data()

            files_count = 0
            for folderName, subfolders, filenames in os.walk(self.storage.hd1()):
                for filename in filenames:
                    file_path =  os.path.join(folderName, filename)
                    if os.path.isfile(file_path):
                        files_count += 1

            data[Status.VAR_FILES_COUNT] = files_count
            data[Status.VAR_FILES_COPIED] = files_count

            files_count = 0
            for key in os.listdir(self.storage.hd2_data()):
                files_count += 1

            data[Status.VAR_FILES_TO_PROCESS] = files_count
            data[Status.VAR_FILES_LEFT_TO_PROCESS] = files_count

            data[Status.VAR_CURRENT_STATUS] = Processing_Status.PHASE_2

        finally:
            Status.lock.release()
            self.save()

        return self

    def add_completed       (self       ): return self.update_counters(FileStatus.COMPLETED          )
    def add_not_supported   (self       ): return self.update_counters(FileStatus.NOT_SUPPORTED      )
    def add_failed          (self       ): return self.update_counters(FileStatus.FAILED             )
    def add_file            (self       ): return self.update_counters(FileStatus.INITIAL            )
    def set_files_count     (self, count): return self.update_counters(FileStatus.NONE        , count)
    def set_not_copied      (self       ): return self.update_counters(FileStatus.NOT_COPIED         )
    def add_in_progress     (self       ): return self.update_counters(FileStatus.IN_PROGRESS        )
    def add_to_be_processed (self       ): return self.update_counters(FileStatus.TO_PROCESS         )

    def get_completed       (self): return self.data().get(Status.VAR_COMPLETED)
    def get_current_status  (self): return self.data().get(Status.VAR_CURRENT_STATUS)
    def get_not_supported   (self): return self.data().get(Status.VAR_NOT_SUPPORTED)
    def get_failed          (self): return self.data().get(Status.VAR_FAILED)
    def get_files_count     (self): return self.data().get(Status.VAR_FILES_COUNT)
    def get_files_copied    (self): return self.data().get(Status.VAR_FILES_COPIED)
    def get_files_to_process(self): return self.data().get(Status.VAR_FILES_TO_PROCESS)
    def get_in_progress     (self): return self.data().get(Status.VAR_IN_PROGRESS)
