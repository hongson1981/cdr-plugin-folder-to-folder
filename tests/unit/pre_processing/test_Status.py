import inspect

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import path_combine, temp_file, file_name
from osbot_utils.utils.Json  import json_load_file
from osbot_utils.utils.Misc import random_text

from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.pre_processing.Processing_Status import Processing_Status
from cdr_plugin_folder_to_folder.pre_processing.Status import FileStatus, Status

from cdr_plugin_folder_to_folder.utils.Logging_Process import process_all_log_entries_and_end_logging_process
from cdr_plugin_folder_to_folder.utils.testing.Temp_Config import Temp_Config


class test_Status(Temp_Config):

    def setUp(self) -> None:
        self.status  = Status()
        self.storage = self.status.storage

    def test__FileStatus(self):
        assert inspect.getmembers(FileStatus, lambda a: type(a) is str) == [  ('COMPLETED'      , 'THE ORIGINAL FILE IS CLEANED'                     ),
                                                                              ('FAILED'         , 'UNABLE TO CLEAN THE FILE'                         ),
                                                                              ('INITIAL'        , 'Initial'                                          ),
                                                                              ('IN_PROGRESS'    , 'In Progress'                                      ),
                                                                              ('NONE'           , 'None'                                             ),
                                                                              ('NOT_COPIED'     , 'Will not be copied'                               ),
                                                                              ('NOT_SUPPORTED'  , 'The file type is not currently supported'         ),
                                                                              ('NO_CLEANING_NEEDED'  , 'THE ORIGINAL FILE WAS ALREADY CLEAN'         ),
                                                                              ('TO_PROCESS'     , 'To Process'                                       ),
                                                                              ('__module__'     , 'cdr_plugin_folder_to_folder.pre_processing.Status')]

    def test_server_status(self):
        # todo write test that confirms that the data has been saved and the status file has been created
        pass

    # error is caused by https://github.com/giampaolo/psutil/issues/1219
    def test_bug_get_server_data_throws_exception_on_psutil_net_connections(self):
        import psutil
        # the issue is MacOS specific. So check if this is MacOS. Stop the test if it is not.
        from sys import platform
        if not platform == 'darwin':
            # Not MacOS
            return
        self.assertRaises(psutil.AccessDenied, self.status.get_server_status)
        try:
            self.status.get_server_status()
        except psutil.AccessDenied as error:
            assert error.__class__.__name__ == 'AccessDenied'
            traces = inspect.trace()
            trace_0 = traces[0]
            # trace_0_class_name = trace_0.frame.f_locals["self"].__class__.__name__
            # assert trace_0.code_context         == ['            self.status.get_server_status()\n']
            # assert trace_0.function             == 'test_bug_get_server_data_throws_exception_on_psutil_net_connections'
            # assert trace_0_class_name           == 'test_Status'
            # assert file_name(trace_0.filename)  == 'test_Status.py'
            # assert trace_0.lineno               == 41

            trace_1 = traces[1]
            assert trace_1.code_context         == ['            self.get_server_data()\n']
            assert trace_1.function             == 'get_server_status'
            assert file_name(trace_1.filename)  == 'Status.py'
            assert trace_1.lineno               == 166

            trace_2 = traces[2]
            assert trace_2.code_context         == ["        self._status_data[Status.VAR_NETWORK_CONNECTIONS] = len(psutil.net_connections(kind='tcp'))\n"]
            assert trace_2.function             == 'get_server_data'
            assert file_name(trace_2.filename)  == 'Status.py'
            assert trace_2.lineno               == 158

            trace_3 = traces[3]
            assert trace_3.code_context         == ['    return _psplatform.net_connections(kind)\n']
            assert trace_3.function             == 'net_connections'
            assert file_name(trace_3.filename)  == '__init__.py'
            assert trace_3.lineno               == 2153

    def test_get_server_data(self):
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
        assert status.reset_system_data().data()             == status.default_data()
        assert status.load_data().reset_system_data().data() == status.default_data()
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