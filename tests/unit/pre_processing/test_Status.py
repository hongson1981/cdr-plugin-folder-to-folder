import inspect

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import path_combine, temp_file
from osbot_utils.utils.Json  import json_load_file
from osbot_utils.utils.Misc import random_text

from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.pre_processing.Status import FileStatus, Processing_Status, Status
from cdr_plugin_folder_to_folder.utils.Logging import log_info, log_debug
from cdr_plugin_folder_to_folder.utils.Logging_Process import process_all_log_entries_and_end_logging_process
from cdr_plugin_folder_to_folder.utils.testing.Temp_Config import Temp_Config


class test_Status(Temp_Config):

    def setUp(self) -> None:
        self.status  = Status()
        self.storage = self.status.storage

    def test__FileStatus(self):
        assert inspect.getmembers(FileStatus, lambda a: type(a) is str) == [  ('COMPLETED'      , 'Completed Successfully'                           ),
                                                                              ('FAILED'         , 'Completed with errors'                            ),
                                                                              ('INITIAL'        , 'Initial'                                          ),
                                                                              ('IN_PROGRESS'    , 'In Progress'                                      ),
                                                                              ('NONE'           , 'None'                                             ),
                                                                              ('NOT_COPIED'     , 'Will not be copied'                               ),
                                                                              ('NOT_SUPPORTED'  , 'The file type in not currently supported'         ),
                                                                              ('TO_PROCESS'     , 'To Process'                                       ),
                                                                              ('__module__'     , 'cdr_plugin_folder_to_folder.pre_processing.Status')]

    def test_server_status(self):
        status = self.status
        status.get_server_status()
        data = status.data()

        assert data[Status.VAR_NUMBER_OF_CPUS] > 0

        cpu_percents = data[Status.VAR_CPU_UTILIZATION]
        assert len(cpu_percents) > 0
        assert isinstance(cpu_percents[0], (int, float))
        assert cpu_percents[0] >= 0

        ram_percent = data[Status.VAR_RAM_UTILIZATION]
        assert isinstance(ram_percent, (int, float))
        assert ram_percent > 0

        processes_count = data[Status.VAR_NUM_OF_PROCESSES]
        assert isinstance(processes_count, (int))
        assert processes_count > 0

        assert data[Status.VAR_NETWORK_CONNECTIONS] >= 0

        assert data[Status.VAR_DISK_PARTITIONS] > 0

    def test_load_data(self):
        status = self.status
        assert status.data()             == status.default_data()
        assert status.load_data().data() == status.default_data()
        assert status.get_files_count()  == 0
        for i in range(1,100):
            assert status.add_completed()
            assert status.get_completed() == i

            assert status.add_failed()
            assert status.get_failed() == i

            assert status.add_file()
            assert status.get_files_copied() == i

            assert status.add_in_progress()
            assert status.get_in_progress() == 1

            assert status.add_to_be_processed()
            assert status.get_files_to_process() == i

            assert status.set_stopped()
            assert status.get_current_status() == Processing_Status.STOPPED

            assert status.set_started()
            assert status.get_current_status() == Processing_Status.STARTED

            assert status.set_phase_1()
            assert status.get_current_status() == Processing_Status.PHASE_1

            assert status.set_phase_2()
            assert status.get_current_status() == Processing_Status.PHASE_2

        assert json_load_file(status.status_file_path()) == status.data()

    def test_status_file_path(self):
        assert self.status.status_file_path() == path_combine(self.storage.hd2_status(), Status.STATUS_FILE_NAME)



    # todo: add multi-threading test
    # def worker(c):
    #     for i in range(2):
    #         r = random.random()
    #         logging.debug('Sleeping %0.02f', r)
    #         time.sleep(r)
    #         c.increment()
    #     logging.debug('Done')
    #
    # if __name__ == '__main__':
    #     counter = Counter()
    #     for i in range(2):
    #         t = threading.Thread(target=worker, args=(counter,))
    #         t.start()
    #
    #     logging.debug('Waiting for worker threads')
    #     main_thread = threading.currentThread()
    #     for t in threading.enumerate():
    #         if t is not main_thread:
    #             t.join()
    #     logging.debug('Counter: %d', counter.value)