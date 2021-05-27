from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

from cdr_plugin_folder_to_folder.common_settings.Config import Config, DEFAULT_THREAD_COUNT
from cdr_plugin_folder_to_folder.metadata.Metadata_Elastic import Metadata_Elastic
from cdr_plugin_folder_to_folder.processing.Loops import Loops
from cdr_plugin_folder_to_folder.pre_processing.Status import Status
from osbot_utils.utils.Json import json_format

import requests

router_params = { "prefix": "/processing"  ,
                  "tags"  : ['Processing'] }

router = APIRouter(**router_params)

@router.post("/start")
def process_hd2_data_to_hd3(thread_count:int=DEFAULT_THREAD_COUNT):
    loops = Loops()
    loops.LoopHashDirectories(thread_count)
    if loops.HasBeenStopped():
        return "Loop stopped"
    return "Loop completed"

@router.post("/start-sequential")
def process_hd2_data_to_hd3_sequential():
    loops = Loops()
    loops.LoopHashDirectoriesSequential()
    if loops.HasBeenStopped():
        return "Loop stopped"
    return "Loop completed"

@router.post("/stop")
def stop_processing():
    loops = Loops()
    loops.StopProcessing()
    return "Loop stopped"

@router.post("/single_file")
def process_single_file():
    loops = Loops()
    loops.ProcessSingleFile()
    return "File has been processed"

@router.get("/status")
def get_the_processing_status():
    status = Status()
    return JSONResponse(status.data())

@router.get("/metrics")
def get_prometheus_metrics():
    config = Config()
    # make sure metrics exist
    status = Status()

    # get the metrics from the prometheus page
    text = 'No metrics'
    try:
        text = requests.get(config.prometheus_url).text
    except Exception as e:
        text = f'Cannot get metrics from {config.prometheus_url}'

    return Response(content=text, media_type="text/plain")
