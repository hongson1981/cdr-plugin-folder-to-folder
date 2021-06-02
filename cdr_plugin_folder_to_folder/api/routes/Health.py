from cdr_plugin_folder_to_folder.api.Server_Status import Server_Status
from cdr_plugin_folder_to_folder.common_settings.Config import Config
from fastapi import APIRouter

router_params = { "prefix": ""  ,
                  "tags"  : ['Health Checks'] }
router = APIRouter(**router_params)

@router.get("/")
def root():
    return health()

@router.get("/health")
def health():
    return { "status": "ok"}

@router.get("/status")
def status():
    return Server_Status().now()

@router.get("/version")
def version():
    return { "version": Config().api_version}