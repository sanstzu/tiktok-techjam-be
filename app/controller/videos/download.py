from tempfile import mkstemp
import os
import app.utils.s3 as s3util
import app.consts as consts
from fastapi.responses import RedirectResponse


TEMP_FILE_DIR = consts.TEMP_FILE_DIR

def get_video_controller(video_id: str):
    os.makedirs(TEMP_FILE_DIR, exist_ok=True)

    bucket_path = f"videos/{video_id}.mp4"

    s3_url = s3util.get_presigned_url(bucket_path, "tiktok-techjam")
    
    return RedirectResponse(url=s3_url) 