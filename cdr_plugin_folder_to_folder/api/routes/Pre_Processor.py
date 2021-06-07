from osbot_utils.utils.Status import status_ok

from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.common_settings.Config import DEFAULT_THREAD_COUNT
from fastapi import APIRouter
from pydantic import BaseModel

router_params = { "prefix": "/pre-processor"  ,
                  "tags"  : ['Pre Processor'] }
router = APIRouter(**router_params)

class DIRECTORY(BaseModel):
    folder     : str = "./test_data/scenario-1/hd1"

class DOWNLOAD_URL(BaseModel):
    url        : str = "http:/download.zip"

@router.post("/start-hd1-watcher-thread")
def start_hd1_watcher_thread():
    pre_processor = Pre_Processor()
    status_message = pre_processor.StartHD1WatcherThread()
    return status_ok(message=status_message)

@router.post("/stop-hd1-watcher-thread")
def stop_hd1_watcher_thread():
    pre_processor = Pre_Processor()
    status_message = pre_processor.StopHD1WatherThread()
    return status_ok(message=status_message)

@router.post("/pre-process")
def pre_process_hd1_data_to_hd2(thread_count:int=DEFAULT_THREAD_COUNT):
    pre_processor = Pre_Processor()
    status_message = pre_processor.process_hd1_files(thread_count)
    return status_ok(message=status_message)

@router.post("/clear-data-and-status")
def clear_data_and_status_folders():
    pre_processor = Pre_Processor()
    status_message = pre_processor.clear_data_and_status_folders()
    return status_ok(message=status_message)

@router.post("/mark-all-hd2-files-unprocessed")
def mark_all_hd2_files_unprocessed():
    pre_processor = Pre_Processor()
    status_message = pre_processor.mark_all_hd2_files_unprocessed()
    return status_ok(message=status_message)

@router.post("/pre_process_folder")
def pre_process_a_folder(item: DIRECTORY):
    pre_processor = Pre_Processor()
    status_message = pre_processor.process_folder(folder_to_process=item.folder)
    return status_ok(message=status_message)

@router.post("/download_and_pre_process_a_zip_file")
def download_and_pre_process_a_zip_file(item: DOWNLOAD_URL):
    pre_processor = Pre_Processor()
    status_message = pre_processor.process_downloaded_zip_file(url=item.url)
    return status_ok(message=status_message)


