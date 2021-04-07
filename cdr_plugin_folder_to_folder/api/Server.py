import logging

import fastapi
import uvicorn
from fastapi import FastAPI

#from cdr_plugin_folder_to_folder.api.users import router
from cdr_plugin_folder_to_folder.processing.main import router as processing_router
from cdr_plugin_folder_to_folder.pre_processing.main import router as pre_processing_router
from cdr_plugin_folder_to_folder.file_distribution.main import router as file_distribution_router

class Server:

    def __init__(self, app):
        self.host       = "0.0.0.0"
        self.log_level  = "info"
        self.port       = 8880                                      # todo: move to globally configurable value (set via Env variables)
        self.app        = app
        self.reload     = True                                      # automatically reloads server on code changes

    def fix_logging_bug(self):
        # there were duplicated entries on logs
        #    - https://github.com/encode/uvicorn/issues/614
        #    - https://github.com/encode/uvicorn/issues/562
        logging.getLogger().handlers.clear()                        # todo: see side effects of this

    def setup(self):
        self.app.include_router(processing_router, prefix="")
        self.app.include_router(pre_processing_router, prefix="")
        self.app.include_router(file_distribution_router, prefix="/get_files")
        self.fix_logging_bug()
        return self

    def start(self):
        uvicorn.run("Server:app", host=self.host, port=int(self.port), log_level=self.log_level, reload=self.reload)


# we need to do this here so that when unicorn reload is enabled the "Server:app" has an fully setup instance of the Server object
app     = FastAPI()
server  = Server(app)
server.setup()

if __name__ == "__main__":
    server.start()