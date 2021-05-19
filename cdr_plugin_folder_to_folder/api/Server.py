import logging
import os

import uvicorn
from fastapi_offline import FastAPIOffline as FastAPI
from starlette.datastructures import Headers, URL
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
#from cdr_plugin_folder_to_folder.api.users import router
from osbot_utils.utils.Misc import to_int
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Scope, Receive, Send

from cdr_plugin_folder_to_folder.api.routes.Processing import router as router_processing
from cdr_plugin_folder_to_folder.api.routes.Pre_Processor import router as router_pre_processing
from cdr_plugin_folder_to_folder.api.routes.File_Distributor import router as router_file_distribution
from cdr_plugin_folder_to_folder.api.routes.Health import router as router_health
from cdr_plugin_folder_to_folder.api.routes.Configure import router as router_configure
from cdr_plugin_folder_to_folder.utils.Logging import log_debug
from cdr_plugin_folder_to_folder.utils.Logging_Process import start_logging
from cdr_plugin_folder_to_folder.pre_processing.Status import Status

class Logging_Middleware:
    def __init__(self, app: ASGIApp, minimum_size: int = 500) -> None:
        self.app = app
        self.minimum_size = minimum_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        headers = Headers(scope=scope)
        url     = URL(scope=scope)
        log_debug(message=f'[API Server] {url}', data={'headers':f'{headers}'})
        await self.app(scope, receive, send)

class Server:

    def __init__(self, app, port="8880", reload=True):
        self.host       = "0.0.0.0"
        self.log_level  = "info"
        self.port       = to_int(port)                                    # todo: move to globally configurable value (set via Env variables)
        self.app        = app
        self.reload     = reload                                              # automatically reloads server on code changes

    def add_routes(self):
        self.app.include_router(router_processing       )
        self.app.include_router(router_pre_processing   )
        self.app.include_router(router_file_distribution)
        self.app.include_router(router_health           )
        self.app.include_router(router_configure        )
        self.fix_logging_bug()
        self.allow_cors()
        return self

    def allow_cors(self):
        self.app.add_middleware(CORSMiddleware, allow_origins     = ["*"],
                                                allow_credentials = True ,
                                                allow_methods     = ["*"],
                                                allow_headers     = ["*"])
        return self

    def fix_logging_bug(self):
        # there were duplicated entries on logs
        #    - https://github.com/encode/uvicorn/issues/614
        #    - https://github.com/encode/uvicorn/issues/562
        logging.getLogger().handlers.clear()                                # todo: see side effects of this

    def start(self):
        log_debug(message=f"Starting API server on {self.host}:{self.port} with uvicorn log level {self.log_level}")
        uvicorn.run("cdr_plugin_folder_to_folder.api.Server:app", host=self.host, port=self.port, log_level=self.log_level, reload=self.reload)

    def setup_logging(self):
        start_logging()
        self.app.add_middleware(Logging_Middleware)
        log_debug(message="[API Server] logging process has started and FastAPI middleware setup")
        return self

    def routes(self):
        routes = {}
        for route in self.app.routes:

            if hasattr(route,"include_in_schema") and route.include_in_schema:
                routes[route.path] = { 'path_format': route.path_format ,
                                       'name'       : route.name        ,
                                       'methods'    : route.methods     }
        return routes

# todo: refactor this into a separate class which can also be used by the individual sections (i.e. tags)
tags_metadata = [
    {"name": "Configuration"   , "description": "Step 0"},
    {"name": "Pre Processor"   , "description": "Step 1"},
    {"name": "Processing"      , "description": "Step 2"},
    {"name": "File Distributor", "description": "Util methods"},
]

# we need to do this here so that when unicorn reload is enabled the "cdr_plugin_folder_to_folder.api.Server:app" has an fully setup instance of the Server object
app     = FastAPI(title="GW Folder-to-Folder API",
                  openapi_tags=tags_metadata)

@app.get("/")
async def docs_redirect():
    response = RedirectResponse(url='/docs')
    return response

server  = Server(app)
server.add_routes()
if "PYTEST_CURRENT_TEST" not in os.environ:
    server.setup_logging()

def run_if_main():
    if __name__ == "__main__":
        server.start()

run_if_main()