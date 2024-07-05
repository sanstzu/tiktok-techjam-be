from tempfile import SpooledTemporaryFile, mkstemp
import app.main as app
import app.utils.s3 as s3util
import time
from fastapi import HTTPException

# For debugging purposes

zero_percent_timestamp = 0

def __get_debug_percentage():
    return app.get_timestamp_percentage()

def get_status_controller(id: str):

    if id is None:
        raise HTTPException(status_code=400, detail="id is required")
    elif id != "testid1":
        raise HTTPException(status_code=404, detail="id not found")
    else:
        # TODO: Get from celery queue to check how many tasks in the group are done
        return f"{__get_debug_percentage():.9f}"