from tempfile import SpooledTemporaryFile, mkstemp
import os
import app.utils.s3 as s3util
import uuid


def get_status_controller(highlight_id: str):
    
    # TODO: Get from celery queue to check how many tasks in the group are done

    return float(0.5)