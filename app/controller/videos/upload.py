from tempfile import SpooledTemporaryFile, mkstemp
import os
import app.utils.s3 as s3util
import uuid

TEMP_FILE_DIR = "./tmp"

async def upload_controller(file: SpooledTemporaryFile):
    file.seek(0)

    os.makedirs(TEMP_FILE_DIR, exist_ok=True)
    tmp_file = mkstemp(None, "upload_", TEMP_FILE_DIR)

    with open(tmp_file[1], "wb") as f:
        f.write(file.read())

    s3_file_name = f"{uuid.uuid4()}.mp4"
    
    s3util.upload_to_bucket(tmp_file[1], "video-1", "tiktok-techjam")