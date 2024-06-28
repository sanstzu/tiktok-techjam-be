from tempfile import SpooledTemporaryFile, mkstemp
import os
import app.utils.s3 as s3util
import uuid


def get_results_controller(highlight_id: str):
    # TODO: Retrieve from database
    # Convert s3 path to signed url    

    return {
        "video_url": ["url1", "url2", "url3"],
    }