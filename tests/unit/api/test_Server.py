import imp
import inspect
from unittest import TestCase
from unittest.mock import patch, call

from fastapi_offline import FastAPIOffline as FastAPI
from osbot_utils.utils.Misc import list_set

from cdr_plugin_folder_to_folder.api.Server import Server
from cdr_plugin_folder_to_folder.utils.testing.Temp_API_Server import Temp_API_Server


class test_Server(TestCase):

    def setUp(self) -> None:
        app = FastAPI()
        self.server = Server(app=app, reload=False)

    #def test_setup(self):
    #    self.server.add_routes()

    @patch("uvicorn.run")
    def test_start(self, mock_run):
        expected_call = call('cdr_plugin_folder_to_folder.api.Server:app',
                              host='0.0.0.0',
                              port=8880,
                              log_level='info',
                              reload=False)
        self.server.start()
        assert mock_run.mock_calls == [expected_call]

    def test_start_stop(self):
        with Temp_API_Server() as api_server:
            assert api_server.server_running() is True
            assert api_server.http_GET()          == api_server.http_GET("/docs")
            assert api_server.http_GET("/health") == {'status': 'ok'}
        assert api_server.server_running() is False

    @patch("uvicorn.run")
    def test_start__via__main(self, mock_run):              # this test confirms that when running the Server directly the uvicorn.run is called
        path_file = inspect.getfile(Server)                 # get path of Server
        imp.load_source('__main__', path_file)              # force reload and set __main__
        assert mock_run.call_count == 1

    # lock the current rules mappings to that any new API changes also require an change to this test
    def test_routes(self):
        # routes before server.add_routes()
        assert [route.path for route in self.server.app.routes] == ['/openapi.json', '/static-offline-docs', '/docs', '/docs/oauth2-redirect', '/redoc']
        assert self.server.routes() == {}
        self.server.add_routes()
        assert self.server.routes() == {  '/'                                                    : { 'methods': {'GET' }, 'name': 'root'                                , 'path_format': '/'                                                    },
                                          '/configuration/config/'                               : { 'methods': {'GET' }, 'name': 'config'                              , 'path_format': '/configuration/config/'                               },
                                          '/configuration/configure_env/'                        : { 'methods': {'POST'}, 'name': 'configure_environment'               , 'path_format': '/configuration/configure_env/'                        },
                                          '/configuration/configure_gw_sdk_endpoints/'           : { 'methods': {'POST'}, 'name': 'configure_multiple_gw_sdk_endpoints' , 'path_format': '/configuration/configure_gw_sdk_endpoints/'           },
                                          '/configuration/reload_elastic_file_metadata/'         : { 'methods': {'PUT' }, 'name': 'reload_elastic_file_metadata'        , 'path_format': '/configuration/reload_elastic_file_metadata/'         },
                                          '/configuration/reload_hash_json/'                     : { 'methods': {'PUT' }, 'name': 'reload_elastic_file_metadata'        , 'path_format': '/configuration/reload_hash_json/'                     },
                                          '/configuration/reload_kibana_dashboards/'             : { 'methods': {'PUT' }, 'name': 'reload_elastic_file_metadata'        ,  'path_format': '/configuration/reload_kibana_dashboards/'            },
                                          '/configuration/reset_logging/'                        : { 'methods': {'PUT' }, 'name': 'reset_logging'                       , 'path_format': '/configuration/reset_logging/'                        },
                                          '/configuration/clear_elastic_file_analysis/'          : {'methods': {'PUT'},   'name': 'clear_elastic_file_analysis'         , 'path_format': '/configuration/clear_elastic_file_analysis/'          },
                                          '/file-distributor/hd2/status'                         : { 'methods': {'GET' }, 'name': 'get_hd2_status_files'                , 'path_format': '/file-distributor/hd2/status'                         },
                                          '/file-distributor/hd2/data'                           : { 'methods': {'GET'},  'name': 'get_hd2_data_files'                  , 'path_format': '/file-distributor/hd2/data'                           },
                                          '/file-distributor/hd2/processed'                      : { 'methods': {'GET'},  'name': 'get_hd2_processed_files'             , 'path_format': '/file-distributor/hd2/processed'                      },
                                          '/health'                                              : { 'methods': {'GET' }, 'name': 'health'                              , 'path_format': '/health'                                              },
                                          '/pre-processor/clear-data-and-status'                 : { 'methods': {'POST'}, 'name': 'clear_data_and_status_folders'       , 'path_format': '/pre-processor/clear-data-and-status'                 },
                                          '/pre-processor/download_and_pre_process_a_zip_file'   : { 'methods': {'POST'}, 'name': 'download_and_pre_process_a_zip_file' , 'path_format': '/pre-processor/download_and_pre_process_a_zip_file'   },
                                          '/pre-processor/mark-all-hd2-files-unprocessed'        : {'methods': {'POST'}, 'name': 'clear_data_and_status_folders'        , 'path_format': '/pre-processor/mark-all-hd2-files-unprocessed'        },
                                          '/pre-processor/pre-process'                           : { 'methods': {'POST'}, 'name': 'pre_process_hd1_data_to_hd2'         , 'path_format': '/pre-processor/pre-process'                           },
                                          '/pre-processor/pre_process_folder'                    : { 'methods': {'POST'}, 'name': 'pre_process_a_folder'                , 'path_format': '/pre-processor/pre_process_folder'                    },
                                          '/processing/single_file'                              : { 'methods': {'POST'}, 'name': 'process_single_file'                 , 'path_format': '/processing/single_file'                              },
                                          '/processing/start'                                    : { 'methods': {'POST'}, 'name': 'process_hd2_data_to_hd3'             , 'path_format': '/processing/start'                                    },
                                          '/processing/start-sequential'                         : { 'methods': {'POST'}, 'name': 'process_hd2_data_to_hd3_sequential'  , 'path_format': '/processing/start-sequential'                         },
                                          '/processing/status'                                   : { 'methods': {'GET' }, 'name': 'get_the_processing_status'           , 'path_format': '/processing/status'                                   },
                                          '/processing/stop'                                     : { 'methods': {'POST'}, 'name': 'stop_processing'                     , 'path_format': '/processing/stop'                                     },
                                          '/status'                                              : { 'methods': {'GET' }, 'name': 'status'                              , 'path_format': '/status'                                              },
                                          '/version'                                             : { 'methods': {'GET' }, 'name': 'version'                             , 'path_format': '/version'                                             }}


    # todo add global exception handler
    #def test__exception_in_method
    # @app.exception_handler(StarletteHTTPException)
    # async def http_exception_handler(request, exc):
    #    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

    # FastAPI allows multiple rules mappings (which should never happen)
    def test__detect_duplicate_routes(self):
        self.server.add_routes()
        paths_format = [route.path for route in self.server.app.routes]
        assert sorted(paths_format) == list_set(paths_format)




