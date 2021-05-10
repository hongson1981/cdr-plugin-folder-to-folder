from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json import str_to_json, json_to_str, json_parse
from osbot_utils.utils.Http import GET_json, GET

from cdr_plugin_folder_to_folder.configure.Configure_Env import Configure_Env

class test_Configure_Env(TestCase):

    def setUp(self):
        self.configure_env = Configure_Env()


    def test_get_valid_endpoints(self):
        url = 'https://tmol8zkg3c.execute-api.eu-west-1.amazonaws.com/prod/sdk-servers/ip_addresses'
        ips = []
        try:
            ips = str(GET_json(url).get('live_ips'))
        except:
            assert False
        ips =  ips.replace("'", '"')

        endpoints = []
        for ip in str_to_json(ips):
            endpoints.append({'IP': ip , "Port": "8080"})

        valid_endpoints = {'Endpoints' : endpoints }
        endpoint_string = json_to_str(valid_endpoints)
        result = self.configure_env.get_valid_endpoints(endpoint_string)
        responsive_endpoints = json_parse(result).get('Endpoints')
        assert len(responsive_endpoints) > 0
        for enpoint in responsive_endpoints:
            assert enpoint in endpoints


