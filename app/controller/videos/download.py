from tempfile import mkstemp
import os
import app.utils.s3 as s3util
import app.consts as consts
from fastapi.responses import FileResponse


TEMP_FILE_DIR = consts.TEMP_FILE_DIR

def get_video_controller(video_id: str):
    os.makedirs(TEMP_FILE_DIR, exist_ok=True)
    tmp_file = mkstemp(None, "upload_", TEMP_FILE_DIR)

    bucket_path = f"videos/{video_id}.mp4"

    s3util.download_from_bucket(tmp_file[1], bucket_path, "tiktok-techjam")
    
    return FileResponse(tmp_file[1], media_type="video/mp4", filename=f"{video_id}.mp4")