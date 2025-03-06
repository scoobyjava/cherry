import time
import logging
from flask import request

logger = logging.getLogger("RequestLogger")
logger.setLevel(logging.INFO)

def log_request_time(app):
    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def log_response(response):
        duration = time.time() - request.start_time
        logger.info(f"{request.method} {request.path} completed in {duration:.3f}s")
        return response

    return app