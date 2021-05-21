import sys
import json
import requests
import ntpath
import os.path
import xmltodict
import zipfile


from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Files import folder_create, parent_folder, file_delete, \
    folder_delete_all, file_unzip, path_append, folder_exists, file_exists, \
    folder_files, file_copy
from osbot_utils.utils.Json import json_save_file_pretty
from datetime import datetime, timedelta

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.Logging import log_error, log_info
from cdr_plugin_folder_to_folder.utils.file_utils import FileService
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.processing.Events_Log import Events_Log
from cdr_plugin_folder_to_folder.processing.Events_Log_Elastic import Events_Log_Elastic
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.pre_processing.Status import Status, FileStatus
from cdr_plugin_folder_to_folder.processing.Report_Elastic import Report_Elastic
from cdr_plugin_folder_to_folder.processing.Analysis_Json import Analysis_Json
from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json

class File_Processing:

    RESP_CODE_NOT_DECODED = "Engine response could not be decoded"

    def __init__(self, events_log, events_elastic, report_elastic, analysis_elastic, meta_service):
        self.meta_service       = meta_service
        self.events_log         = events_log
        self.events_elastic     = events_elastic
        self.report_elastic     = report_elastic
        self.sdk_api_version    = "Not available"
        self.sdk_engine_version = "Not available"

        self.analysis_json      = Analysis_Json()
        self.analysis_elastic   = analysis_elastic
        self.config             = Config()
        self.hash_json          = Hash_Json()
        self.status             = Status()
        self.storage            = Storage()




    def add_event_log(self, message, event_data = {}):
        json_data = self.events_log.add_log(message, event_data)
        self.events_elastic.add_event_log(json_data)

    def base64request(self, endpoint, api_route, base64enc_file):
        try:
            url = endpoint + "/" + api_route

            payload = json.dumps({
              "Base64": base64enc_file
            })

            headers = {
              'Content-Type': 'application/json'
            }

            return requests.request("POST", url, headers=headers, data=payload, timeout=int(self.config.request_timeout))
     
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

            response = requests.request("GET", url, headers=headers, data=payload, timeout=int(self.config.request_timeout))
            return response.text

        except Exception as e:
            raise ValueError(str(e))

    def rebuild (self, endpoint, base64enc_file):
        return self.base64request(endpoint, "api/rebuild/base64", base64enc_file)

    def rebuild_zip (self, endpoint, base64enc_file):
        return self.base64request(endpoint, "api/analyse/rebuild-zip-from-base64", base64enc_file)

    def convert_xml_report_to_json(self, dir, xmlreport):
        if not xmlreport:
            raise ValueError('Failed to obtain the XML report')

        try:
            json_obj = xmltodict.parse(xmlreport)

            file_extension = json_obj["gw:GWallInfo"]["gw:DocumentStatistics"]["gw:DocumentSummary"]["gw:FileType"]
            self.meta_service.set_rebuild_file_extension(dir, file_extension)
            json_obj['original_hash'] = os.path.basename(dir)
            json_save_file_pretty(json_obj, os.path.join(dir, "report.json"))


            #self.report_elastic.add_report(json_obj)

            analysis_obj=self.analysis_json.get_file_analysis(os.path.basename(dir), json_obj)
            json_save_file_pretty(analysis_obj, os.path.join(dir, "analysis.json"))

            self.analysis_elastic.add_analysis(analysis_obj)

            return True
        except Exception as error:
            log_error(message=f"Error in parsing xmlreport: {error}")
            return False

    def get_xmlreport(self, endpoint, fileId, dir):
        log_info(message=f"getting XML Report for {fileId} at {endpoint}")

        xmlreport = self.xmlreport_request(endpoint, fileId)

        return self.convert_xml_report_to_json(dir, xmlreport)

    def get_xmlreport_from_file(self, file_path, dir):
        log_info(message=f"getting XML Report from file {file_path}")

        xmlfile = open(file_path,"r+")
        xmlreport = xmlfile.read()

        return self.convert_xml_report_to_json(dir, xmlreport)

    # Save to HD3
    def save_file(self, result, processed_path):
        self.add_event_log('Saving to: ' + processed_path)

        dirname = ntpath.dirname(processed_path)
        basename = ntpath.basename(processed_path)
        folder_create(dirname)

        decoded = FileService.base64decode(result)

        if decoded:
            FileService.wrtie_binary_file(dirname, basename, decoded)
            self.add_event_log('The decoded file has been saved')
            return processed_path
        else:
            FileService.wrtie_file(dirname, basename + ".html", result)                     # todo: capture better this workflow
            self.add_event_log('Decoding FAILED. The HTML file has been saved')
            return processed_path + '.html'                                                 # todo: refactor this workflow and how this is calculated

    def get_server_version(self, dir, headers):

        SDKEngineVersionKey = "X-SDK-Engine-Version"
        SDKAPIVersionKey = "X-SDK-Api-Version"

        sdk_engine_version = ""
        sdk_api_version = ""

        if SDKEngineVersionKey in headers:
            sdk_engine_version = headers[SDKEngineVersionKey]
        if SDKAPIVersionKey in headers:
            sdk_api_version = headers[SDKAPIVersionKey]

        if not sdk_engine_version and not sdk_api_version:
            return

        self.meta_service.set_server_version(dir, "Engine:" + sdk_engine_version + " API:" + sdk_api_version )

    # legacy version (makes two calls to get the data)
    @log_duration
    def do_rebuild(self, endpoint, hash, source_path, dir):
        log_info(message=f"Starting rebuild for file {hash} on endpoint {endpoint}")
        with Duration() as duration:
            event_data = {"endpoint": endpoint, "hash": hash, "source_path": source_path, "dir": dir } # todo: see if we can use a variable that holds the params data
            self.add_event_log('Starting File rebuild', event_data)

            self.meta_service.set_rebuild_server(dir, endpoint)

            encodedFile = FileService.base64encode(source_path)
            if not encodedFile:
                message = f"Failed to encode the file: {hash}"
                log_error(message=message)
                self.add_event_log(message)
                self.meta_service.set_error(dir,message)
                return False

            response = self.rebuild(endpoint, encodedFile)
            result = response.text
            if not result:
                message = f"Failed to rebuild the file : {hash}"
                log_error(message=message)
                self.add_event_log(message)
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
                    message = File_Processing.RESP_CODE_NOT_DECODED
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
                    self.add_event_log('The XML report has been saved')
                    self.meta_service.set_xml_report_status(dir, "Obtained")
                else:
                    self.meta_service.set_xml_report_status(dir, "No XML Report")
            else:
                self.meta_service.set_xml_report_status(dir, "Failed to obtain")
                message = f'No X-Adaptation-File-Id header found in the response for {hash}'
                log_error(message)
                self.add_event_log(message)
                self.meta_service.set_error(dir, message)
                return False
                #raise ValueError("No X-Adaptation-File-Id header found in the response")

            self.get_server_version(dir, headers)

        log_info(message=f"rebuild ok for file {hash} on endpoint {endpoint} took {duration.seconds()} seconds")
        return True

    # todo: refactor this method into smaller methods (for each step of the workflow below)
    @log_duration
    def do_rebuild_zip(self, endpoint, hash, source_path, dir):
        log_info(message=f"Starting rebuild for file {hash} on endpoint {endpoint}")

        retvalue = False

        with Duration() as duration:
            event_data = {"endpoint": endpoint, "hash": hash, "source_path": source_path, "dir": dir } # todo: see if we can use a variable that holds the params data
            self.add_event_log('Starting File rebuild', event_data)
            self.meta_service.set_rebuild_server(dir, endpoint)

            encodedFile = FileService.base64encode(source_path)
            if not encodedFile:
                message = f"Failed to encode the file: {hash}"
                log_error(message=message)
                self.add_event_log(message)
                self.meta_service.set_error(dir,message)
                return False

            #with open(rebuild_file_path + ".txt", 'w') as file:
            #    file.write(encodedFile)

            response = self.    rebuild_zip(endpoint, encodedFile)
            zip_file_path = os.path.join(dir, "rebuild.zip")

            headers = response.headers
            self.get_server_version(dir, headers)

            fileIdKey = "X-Adaptation-File-Id"

            unzip_folder_path = path_append(dir, headers[fileIdKey])

            try:
                with open(zip_file_path, 'wb') as file:
                    file.write(response.content)

                file_unzip(zip_file_path, dir)

                while True:
                    if not folder_exists(unzip_folder_path):
                        log_error (f"folder not found {unzip_folder_path}")
                        break

                    ## Handle the report
                    report_folder_path = path_append(unzip_folder_path, "report")
                    if not folder_exists(report_folder_path):
                        log_error (f"folder not found {report_folder_path}")
                        break

                    xmlreport_path = os.path.join(report_folder_path, "report.xml")
                    if not file_exists(xmlreport_path):
                        log_error (f"file not found {xmlreport_path}")
                        break

                    self.get_xmlreport_from_file(xmlreport_path, dir)

                    ## Handle the file
                    clean_folder_path = path_append(unzip_folder_path, "clean")
                    if not folder_exists(clean_folder_path):
                        log_error (f"folder not found {clean_folder_path}")
                        break

                    clean_files = folder_files(clean_folder_path)
                    if len(clean_files) != 1:
                        log_error(f"Unexpected number of files in clean folder: {len(clean_files)}")
                        break

                    clean_file_path = path_append(clean_folder_path, clean_files[0])
                    if not file_exists(clean_file_path):
                        log_error (f"file not found {clean_file_path}")
                        break

                    file_size    = os.path.getsize(clean_file_path)                 # calculate rebuilt file fize
                    rebuild_hash = self.meta_service.file_hash(clean_file_path)     # calculate hash of final_rebuild_file_path

                    self.meta_service.set_rebuild_file_size(dir, file_size)
                    self.meta_service.set_rebuild_file_path(dir, clean_file_path)   # capture final_rebuild_file_path
                    self.meta_service.set_rebuild_hash(dir, rebuild_hash)           # capture it

                    for path in self.meta_service.get_original_file_paths(dir):
                        if path.startswith(self.config.hd1_location):
                            rebuild_file_path = path.replace(self.config.hd1_location, self.config.hd3_location)
                        else:
                            rebuild_file_path = os.path.join(self.config.hd3_location, path)

                        folder_create(parent_folder(rebuild_file_path))                         # make sure parent folder exists

                        file_copy(clean_file_path, rebuild_file_path)     # returns actual file saved (which could be .html)

                    retvalue = True
                    break

            except Exception as error:
                message=f"Error in do_rebuild_zip for {hash} : {error}"
                if "is not a zip file" in message:
                    message = "Error while processing the request. See details in 'error.json'"
                    try:
                        file_copy(zip_file_path, os.path.join(dir, "error.json"))
                    except:
                        pass
                log_error(message=message)
                self.meta_service.set_xml_report_status(dir, "No Report")
                self.meta_service.set_error(dir,message)
            finally:
                # clean it up
                if file_exists(zip_file_path):
                    file_delete(zip_file_path)
                if folder_exists(unzip_folder_path):
                    folder_delete_all(unzip_folder_path)
        if retvalue:
            log_info(message=f"rebuild ok for file {hash} on endpoint {endpoint} took {duration.seconds()} seconds")
        return retvalue

    def finalize_completed(self, dir, hash):
        self.status.add_completed()
        metadata = self.meta_service.get_from_file(dir)
        if metadata.get_original_hash() == metadata.get_rebuild_hash():
            self.meta_service.set_status(dir, FileStatus.NO_CLEANING_NEEDED)
            self.hash_json.update_status(hash, FileStatus.NO_CLEANING_NEEDED)
        else:
            self.meta_service.set_status(dir, FileStatus.COMPLETED)
            self.hash_json.update_status(hash, FileStatus.COMPLETED)
        self.meta_service.set_error(dir, "none")

    def finalize_failed(self, dir, hash):
        self.status.add_failed()
        self.meta_service.set_status(dir, FileStatus.FAILED)
        self.hash_json.update_status(hash, FileStatus.FAILED)

    def finalize_not_supported(self, dir, hash):
        self.status.add_not_supported()
        self.meta_service.set_status(dir, FileStatus.NOT_SUPPORTED)
        self.hash_json.update_status(hash, FileStatus.NOT_SUPPORTED)

        if not self.config.save_unsupported_file_types:
            self.events_log.add_log("Will not be copied to hd3")
            return

        for path in self.meta_service.get_original_file_paths(dir):

            rebuild_file_path = self.config.hd3_location
            if path.startswith(self.config.hd1_location):
                rebuild_file_path = path.replace(self.config.hd1_location, self.config.hd3_location)
                original_path     = path
            else:
                rebuild_file_path = self.storage.hd3(path)
                original_path     = self.storage.hd1(path)
            self.events_log.add_log(f"Copying {original_path} to {rebuild_file_path}")
            # make sure parent folder exists
            folder_create(parent_folder(rebuild_file_path))
            file_copy(original_path , rebuild_file_path)

    @log_duration
    def processDirectory (self, endpoint, dir, use_rebuild_zip=False):
        self.add_event_log("Processing Directory: " + dir)
        hash = ntpath.basename(dir)
        if len(hash) != 64:
            self.add_event_log("Unexpected hash length")
            #raise ValueError("Unexpected hash length")
            return False

        metadata_file_path = os.path.join(dir, Metadata_Service.METADATA_FILE_NAME)
        if not (FileService.file_exist(metadata_file_path)):
            self.add_event_log("The metadate.json file does not exist")
            #raise ValueError("The metadate.json file does not exist")
            return False

        if self.meta_service.is_completed_status(dir):
            self.add_event_log("Metadata is in the COMPLETED state")
            return False

        self.add_event_log("Set metadata status IN_PROGRESS")
        self.meta_service.set_status_inprogress(dir)
        self.status.add_in_progress()

        source_path = os.path.join(dir, "source")
        if not (FileService.file_exist(source_path)):
            self.add_event_log("File does not exist")
            #raise ValueError("File does not exist")
            return False

        self.add_event_log("Sending to rebuild")
        tik = datetime.now()
        if use_rebuild_zip:
            status = self.do_rebuild_zip(endpoint, hash, source_path, dir)
        else:
            status = self.do_rebuild(endpoint, hash, source_path, dir)

        #status = self.do_rebuild_zip(endpoint, hash, source_path, dir)

        self.meta_service.get_from_file(dir)
        metadata = self.meta_service.metadata

        if status:
            self.finalize_completed(dir,hash)
        else:
            if not metadata.get_original_file_extension() in self.config.supported_file_types:
                self.finalize_not_supported(dir,hash)
            else:
                self.finalize_failed(dir,hash)
        tok = datetime.now()
        delta = tok - tik
        self.meta_service.set_rebuild_file_duration(dir, delta.total_seconds())

        return True


