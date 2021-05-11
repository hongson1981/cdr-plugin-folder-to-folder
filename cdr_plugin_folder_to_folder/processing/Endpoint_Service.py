import threading
import logging as logger
from time import sleep

from cdr_plugin_folder_to_folder.common_settings.Config    import Config
from cdr_plugin_folder_to_folder.configure.Configure_Env   import Configure_Env
#from cdr_plugin_folder_to_folder.storage.Storage           import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration        import log_duration

from osbot_utils.utils.Http import GET_json, GET
from osbot_utils.utils.Json import str_to_json, json_to_str, json_parse

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
            self.configure_env  = Configure_Env()
            #self.storage        = Storage()
            self.service_thread_on = False
            self.service_thread = threading.Thread()
            self.endpoints      =  []
            self.endpoint_index =  0

    @classmethod
    def clear_instance(cls):
        del cls.instance

    def get_ips(self):
        url = self.config.sdk_servers_api
        ips = []
        try:
            ips = str(GET_json(url).get('live_ips'))
        except:
            ips = ""
        ips = ips.replace("'", '"')
        return ips

    def get_endpoints(self):
        ips = self.get_ips()
        endpoints =  []
        for ip in str_to_json(ips):
            endpoints.append({'IP': ip , "Port": "8080"})
        if 0 == len(endpoints):
            endpoints = self.config.endpoints["Endpoints"]

        valid_endpoints = {'Endpoints' : endpoints }
        endpoint_string = json_to_str(valid_endpoints)
        result = self.configure_env.get_valid_endpoints(endpoint_string)
        endpoints = json_parse(result).get('Endpoints')

        if self.endpoints != endpoints:
            self.reset()
            self.endpoints = endpoints

    def endpoints_count(self):
        return len(self.endpoints)

    def get_endpoint(self):
        endpoint = None

        Endpoint_Service.lock.acquire()
        try:
            if self.endpoints_count():
                endpoint = self.endpoints[self.endpoint_index]
                self.endpoint_index = (self.endpoint_index + 1) % self.endpoints_count()
        finally:
            Endpoint_Service.lock.release()

        return endpoint

    def get_endpoint_url(self):
        endpoint = self.get_endpoint()
        if not endpoint:
            return None
        return "http://" + endpoint['IP'] + ":" + endpoint['Port']

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
        self.endpoint_index = 0
        return self

    def save(self):
        return self

    def update_endpoints_list(self):
        Endpoint_Service.lock.acquire()
        try:
            self.get_endpoints()
        finally:
            Endpoint_Service.lock.release()

        return self
