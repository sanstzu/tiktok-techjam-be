from tempfile import SpooledTemporaryFile, mkstemp
import os
import app.utils.s3 as s3util
import uuid
import app.consts as consts

TEMP_FILE_DIR = consts.TEMP_FILE_DIR

def upload_controller(file: SpooledTemporaryFile):
    file.seek(0)

    os.makedirs(TEMP_FILE_DIR, exist_ok=True)
    tmp_file = mkstemp(None, "upload_", TEMP_FILE_DIR)

    with open(tmp_file[1], "wb") as f:
        f.write(file.read())

    video_id = uuid.uuid4()

    s3_file_name = f"{video_id}.mp4"

    s3_file_path = f"videos/{s3_file_name}"

    # TODO: Add filename and id to database
    # Possible schema videos(id, user_id, s3_video_path, s3_thumbnail_path, created_at)

    # TODO: Add thumbnail to bucket
    
    # Send to worker
    s3util.upload_to_bucket(tmp_file[1], s3_file_path, "tiktok-techjam")

    return video_id