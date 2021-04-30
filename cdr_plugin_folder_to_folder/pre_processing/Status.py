import threading
import psutil
import logging as logger

from osbot_utils.utils.Files                        import path_combine, folder_create, file_create
from osbot_utils.utils.Json                         import json_save_file_pretty, json_load_file, file_exists
from cdr_plugin_folder_to_folder.storage.Storage    import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration

logger.basicConfig(level=logger.INFO)

class FileStatus:                                     # todo move to separate file (either per enum or with all enums)
    INITIAL     = "Initial"
    IN_PROGRESS = "In Progress"
    COMPLETED   = "Completed Successfully"
    FAILED      = "Completed with errors"
    TO_PROCESS  = "To Process"
    NONE        = "None"


class Processing_Status:
    STOPPED = "Stopped"
    STARTED = "Started"
    PHASE_1 = "PHASE 1 - Copying Files"
    PHASE_2 = "PHASE 2 - Rebuilding Files"

class Status:

    STATUS_FILE_NAME             = "status.json"
    VAR_COMPLETED                = "completed"
    VAR_CURRENT_STATUS           = "current_status"
    VAR_FAILED                   = "failed"
    VAR_FILES_TO_PROCESS         = "files_to_process"
    VAR_FILES_LEFT_TO_PROCESS    = "files_left_to_process"
    VAR_FILES_COUNT              = "files_count"
    VAR_FILES_COPIED             = "files_copied"
    VAR_FILES_TO_BE_COPIED       = "files_left_to_be_copied"
    VAR_IN_PROGRESS              = "in_progress"
    VAR_CPU_UTILIZATION          = "cpu_utilization"
    VAR_RAM_UTILIZATION          = "memory_utilization"
    VAR_NUM_OF_PROCESSES         = "number_of_processes"
    VAR_NUM_OF_THREADS           = "number_of_threads"

    lock = threading.Lock()

    _instance = None
    def __new__(cls):                                               # singleton pattern
        if cls._instance is None:
            cls._instance = super(Status, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_status_data') is False:                     # only set these values first time around
            self.storage        = Storage()
            #self._on_save      = []                             # todo: add support for firing up events when data is saved
            self._status_data   = self.default_data()
            self.load_data()

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
                    Status.VAR_FAILED                 : 0               ,
                    Status.VAR_IN_PROGRESS            : 0               ,
                    Status.VAR_CPU_UTILIZATION        : None            ,
                    Status.VAR_RAM_UTILIZATION        : None            ,
                    Status.VAR_NUM_OF_PROCESSES       : None            ,
                    Status.VAR_NUM_OF_THREADS         : None            ,
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

    def get_server_status(self):
        Status.lock.acquire()
        try:
            data = self.data()

            data[Status.VAR_CPU_UTILIZATION] = psutil.cpu_percent(interval=1, percpu=True)
            data[Status.VAR_RAM_UTILIZATION] = psutil.virtual_memory().percent
            data[Status.VAR_NUM_OF_PROCESSES] = len(psutil.pids())
            data[Status.VAR_NUM_OF_THREADS] = 0
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
    def set_stopped      (self       ): return self.set_processing_status(Processing_Status.STOPPED  )
    def set_phase_1      (self       ): return self.set_processing_status(Processing_Status.PHASE_1  )
    def set_phase_2      (self       ): return self.set_processing_status(Processing_Status.PHASE_2  )

    def update_counters(self, updated_status, count=0):
        Status.lock.acquire()
        try:
            data = self.data()
            #data[Status.VAR_CURRENT_STATUS] = updated_status

            if updated_status == FileStatus.NONE:
                data[Status.VAR_FILES_COUNT] += count
                data[Status.VAR_FILES_TO_BE_COPIED] += count
                
            elif updated_status == FileStatus.INITIAL:
                data[Status.VAR_FILES_COPIED] += 1
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

    def add_completed       (self       ): return self.update_counters(FileStatus.COMPLETED          )
    def add_failed          (self       ): return self.update_counters(FileStatus.FAILED             )
    def add_file            (self       ): return self.update_counters(FileStatus.INITIAL            )
    def add_files_count     (self, count): return self.update_counters(FileStatus.NONE        , count)
    def add_in_progress     (self       ): return self.update_counters(FileStatus.IN_PROGRESS        )
    def add_to_be_processed (self       ): return self.update_counters(FileStatus.TO_PROCESS         )

    def get_completed       (self): return self.data().get(Status.VAR_COMPLETED)
    def get_current_status  (self): return self.data().get(Status.VAR_CURRENT_STATUS)
    def get_failed          (self): return self.data().get(Status.VAR_FAILED)
    def get_files_count     (self): return self.data().get(Status.VAR_FILES_COUNT)
    def get_files_copied    (self): return self.data().get(Status.VAR_FILES_COPIED)
    def get_files_to_process(self): return self.data().get(Status.VAR_FILES_TO_PROCESS)
    def get_in_progress     (self): return self.data().get(Status.VAR_IN_PROGRESS)
