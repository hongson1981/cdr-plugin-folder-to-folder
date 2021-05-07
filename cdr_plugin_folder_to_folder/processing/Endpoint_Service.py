import threading
import logging as logger
from time import sleep

from cdr_plugin_folder_to_folder.common_settings.Config    import Config
#from cdr_plugin_folder_to_folder.storage.Storage           import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration        import log_duration

from osbot_utils.utils.Http import GET_json, GET

logger.basicConfig(level=logger.INFO)

class Endpoint_Service:

    lock = threading.Lock()

    _instance = None
    def __new__(cls):                                               # singleton pattern
        if cls._instance is None:
            cls._instance = super(Endpoint_Service, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'instantiated') is False:                     # only set these values first time around
            self.instantiated   = True
            self.config         = Config()
            #self.storage        = Storage()
            self.service_thread_on = False
            self.service_thread = threading.Thread()
            self.endpoints      =  []
            self.endpoint_index =  0

    @classmethod
    def clear_instance(cls):
        del cls.instance

    def get_endpoints(self):
        url = self.config.sdk_servers_api
        ips = []
        try:
            ips = str(GET_json(url).get('live_ips'))
        except:
            pass
        self.endpoints =  []
        for ip in ips:
            self.endpoints.append({'IP': ip , "Port": "8080"})
        if 0 == len(self.endpoints):
            self.endpoints = self.config.endpoints["Endpoints"]

    def endpoints_count(self):
        return len(self.endpoints)

    def get_endpoint(self):
        endpoint = self.endpoints[self.endpoint_index]
        self.endpoint_index = (self.endpoint_index + 1) % self.endpoints_count()
        return endpoint

    def ServiceThread(self, update_interval):
        while self.service_thread_on:
            self.update_endpoints_list()
            sleep(update_interval)

    def StartServiceThread(self):
        if self.service_thread_on:
            return

        self.service_thread_on = True
        self.service_thread = threading.Thread(target=self.ServiceThread, args=(1,))
        self.service_thread.start()

    def StopServiceThread(self):
        self.service_thread_on = False
        self.service_thread.join()

    def load_data(self):
        return self

    def reset(self):
        self.endpoints =  []
        return self

    def save(self):
        return self

    def update_endpoints_list(self):
        Endpoint_Service.lock.acquire()
        try:
            pass
        finally:
            Endpoint_Service.lock.release()
            self.save()

        return self
