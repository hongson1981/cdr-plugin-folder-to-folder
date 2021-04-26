import sys
import json
import requests
import ntpath
import os.path
import xmltodict
from osbot_utils.testing.Duration import Duration

from osbot_utils.utils.Files import folder_create, parent_folder
from osbot_utils.utils.Json import json_save_file_pretty
from datetime import datetime, timedelta

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.Logging import log_error, log_info
from cdr_plugin_folder_to_folder.utils.file_utils import FileService
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.processing.Events_Log import Events_Log
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.pre_processing.Status import Status, FileStatus
from cdr_plugin_folder_to_folder.processing.Report_Elastic import Report_Elastic
from cdr_plugin_folder_to_folder.processing.Analysis_Json import Analysis_Json

class File_Processing:

    def __init__(self, events_log, report_elastic, meta_service):
        self.meta_service   = meta_service
        self.events_log     = events_log
        self.storage        = Storage()
        self.config         = Config()
        self.status         = Status()
        self.report_elastic = report_elastic
        self.sdk_api_version    = "Not available"
        self.sdk_engine_version = "Not available"

        self.analysis_json  = Analysis_Json()

    def base64request(self, endpoint, api_route, base64enc_file):
        try:
            url = endpoint + "/" + api_route

            payload = json.dumps({
              "Base64": base64enc_file
            })

            headers = {
              'Content-Type': 'application/json'
            }

            return requests.request("POST", url, headers=headers, data=payload, timeout=self.config.request_timeout)
     
        except Exception as e:
            log_error(str(e))
            raise ValueError(str(e))

    def xmlreport_request(self, endpoint, fileID):
        try:
            url = endpoint + "/api/Analyse/xmlreport?fileId=" + fileID

            payload = ""
            headers = {
                'Content-Type': 'application/octet-stream'
            }

            response = requests.request("GET", url, headers=headers, data=payload, timeout=self.config.request_timeout)
            return response.text

        except Exception as e:
            raise ValueError(str(e))

    def rebuild (self, endpoint, base64enc_file):
        return self.base64request(endpoint, "api/rebuild/base64", base64enc_file)

    def get_xmlreport(self, endpoint, fileId, dir):
        log_info(message=f"getting XML Report for {fileId} at {endpoint}")

        xmlreport = self.xmlreport_request(endpoint, fileId)
        if not xmlreport:
            raise ValueError('Failed to obtain the XML report')

        try:
            json_obj = xmltodict.parse(xmlreport)

            file_extension = json_obj["gw:GWallInfo"]["gw:DocumentStatistics"]["gw:DocumentSummary"]["gw:FileType"]
            self.meta_service.set_rebuild_file_extension(dir, file_extension)
            json_obj['original_hash'] = os.path.basename(dir)
            json_save_file_pretty(json_obj, os.path.join(dir, "report.json"))

            #self.report_elastic.add_report(json_obj)

            self.analysis_json.update_report(os.path.basename(dir), json_obj)
            return True
        except Exception as error:
            log_error(message=f"Error in parsing xmlreport for {fileId} : {error}")
            return False

    # Save to HD3
    def save_file(self, result, processed_path):
        self.events_log.add_log('Saving to: ' + processed_path)

        dirname = ntpath.dirname(processed_path)
        basename = ntpath.basename(processed_path)
        folder_create(dirname)

        decoded = FileService.base64decode(result)

        if decoded:
            FileService.wrtie_binary_file(dirname, basename, decoded)
            self.events_log.add_log('The decoded file has been saved')
            return processed_path
        else:
            FileService.wrtie_file(dirname, basename + ".html", result)                     # todo: capture better this workflow
            self.events_log.add_log('Decoding FAILED. The HTML file has been saved')
            return processed_path + '.html'                                                 # todo: refactor this workflow and how this is calculated

    @log_duration
    def do_rebuild(self, endpoint, hash, source_path, dir):
        log_info(message=f"Starting rebuild for file {hash} on endpoint {endpoint}")
        with Duration() as duration:
            event_data = {"endpoint": endpoint, "hash": hash, "source_path": source_path, "dir": dir } # todo: see if we can use a variable that holds the params data
            self.events_log.add_log('Starting File rebuild', event_data)

            self.meta_service.set_rebuild_server(dir, endpoint)

            encodedFile = FileService.base64encode(source_path)
            if not encodedFile:
                message = f"Failed to encode the file: {hash}"
                log_error(message=message)
                self.events_log.add_log(message)
                self.meta_service.set_error(dir,message)
                return False

            response = self.rebuild(endpoint, encodedFile)
            result = response.text
            if not result:
                message = f"Failed to rebuild the file : {hash}"
                log_error(message=message)
                self.events_log.add_log(message)
                self.meta_service.set_error(dir, message)
                return False

            try:
                for path in self.meta_service.get_original_file_paths(dir):
                    #rebuild_file_path = path
                    if path.startswith(self.config.hd1_location):
                        rebuild_file_path = path.replace(self.config.hd1_location, self.config.hd3_location)
                    else:
                        rebuild_file_path = os.path.join(self.config.hd3_location, path)

                    folder_create(parent_folder(rebuild_file_path))                         # make sure parent folder exists

                    final_rebuild_file_path = self.save_file(result, rebuild_file_path)     # returns actual file saved (which could be .html)

                    # todo: improve the performance of these update since each will trigger a save
                    file_size    = os.path.getsize(final_rebuild_file_path)                 # calculate rebuilt file fize
                    rebuild_hash = self.meta_service.file_hash(final_rebuild_file_path)     # calculate hash of final_rebuild_file_path

                    self.meta_service.set_rebuild_file_size(dir, file_size)
                    self.meta_service.set_rebuild_file_path(dir, final_rebuild_file_path)   # capture final_rebuild_file_path
                    self.meta_service.set_rebuild_hash(dir, rebuild_hash)                   # capture it
                if not FileService.base64decode(result):
                    message = f"Engine response could not be decoded"
                    log_error(message=message, data=f"{result}")
                    self.meta_service.set_error(dir,message)
                    return False
            except Exception as error:
                message=f"Error Saving file for {hash} : {error}"
                log_error(message=message)
                self.meta_service.set_xml_report_status(dir, "No Report")
                self.meta_service.set_error(dir,message)
                return False

            headers = response.headers
            fileIdKey = "X-Adaptation-File-Id"

            # get XML report
            if fileIdKey in headers:
                if self.get_xmlreport(endpoint, headers[fileIdKey], dir):
                    self.events_log.add_log('The XML report has been saved')
                    self.meta_service.set_xml_report_status(dir, "Obtained")
                else:
                    self.meta_service.set_xml_report_status(dir, "No XML Report")
            else:
                self.meta_service.set_xml_report_status(dir, "Failed to obtain")
                message = f'No X-Adaptation-File-Id header found in the response for {hash}'
                log_error(message)
                self.events_log.add_log(message)
                self.meta_service.set_error(dir, message)
                return False
                #raise ValueError("No X-Adaptation-File-Id header found in the response")

            # todo: add when server side supports this
            # SDKEngineVersionKey = "X-SDK-Engine-Version"
            # SDKAPIVersionKey = "X-SDK-Api-Version"
            #
            # if SDKEngineVersionKey in headers:
            #     self.sdk_engine_version = headers[SDKEngineVersionKey]
            # if SDKAPIVersionKey in headers:
            #     self.sdk_api_version = headers[SDKAPIVersionKey]
            #
            # self.meta_service.set_server_version(dir, "Engine:" + self.sdk_engine_version + " API:" + self.sdk_api_version )
        log_info(message=f"rebuild ok for file {hash} on endpoint {endpoint} took {duration.seconds()} seconds")
        return True

    @log_duration
    def processDirectory (self, endpoint, dir):
        self.events_log.add_log("Processing Directory: " + dir)
        hash = ntpath.basename(dir)
        if len(hash) != 64:
            self.events_log.add_log("Unexpected hash length")
            #raise ValueError("Unexpected hash length")
            return False

        metadata_file_path = os.path.join(dir, Metadata_Service.METADATA_FILE_NAME)
        if not (FileService.file_exist(metadata_file_path)):
            self.events_log.add_log("The metadate.json file does not exist")
            #raise ValueError("The metadate.json file does not exist")
            return False

        if not self.meta_service.is_initial_status(dir):
            self.events_log.add_log("Metadata not in the INITIAL state")
            return False

        self.meta_service.set_status_inprogress(dir)
        self.status.add_in_progress()

        source_path = os.path.join(dir, "source")
        if not (FileService.file_exist(source_path)):
            self.events_log.add_log("File does not exist")
            #raise ValueError("File does not exist")
            return False

        self.events_log.add_log("Sending to rebuild")
        tik = datetime.now()
        status = self.do_rebuild(endpoint, hash, source_path, dir)
        if status:
            self.meta_service.set_status(dir, FileStatus.COMPLETED)
            self.meta_service.set_error(dir, "none")
        else:
            self.meta_service.set_status(dir, FileStatus.FAILED)
        tok = datetime.now()
        delta = tok - tik
        self.meta_service.set_rebuild_file_duration(dir, str(delta))

        return status
