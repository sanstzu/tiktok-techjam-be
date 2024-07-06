from tempfile import SpooledTemporaryFile, mkstemp
import os
import app.utils.s3 as s3util
import uuid
import json
import app.consts as consts
from fastapi import HTTPException
from typing import List
import app.main as app
import hashlib

TEMP_FILE_DIR = consts.TEMP_FILE_DIR
BUF_SIZE = consts.BUF_SIZE

async def upload_controller(file: SpooledTemporaryFile, prompt: List[str]):
    if file is None:
        raise HTTPException(status_code=400, detail="file is required")

    
    file.seek(0)

    os.makedirs(TEMP_FILE_DIR, exist_ok=True)
    tmp_file = mkstemp(None, "upload_", TEMP_FILE_DIR)

    sha256 = hashlib.sha256()

    with open(tmp_file[1], "wb") as f:
        while True:
            data = file.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
            f.write(data)


    video_id = sha256.hexdigest()

    s3_file_name = f"{video_id}.mp4"

    s3_file_path = f"videos/{s3_file_name}"

    if s3util.check_file_exists(s3_file_path, "tiktok-techjam"):
        # Cache and do not upload again
        pass
    else:
        s3util.upload_to_bucket(tmp_file[1], s3_file_path, "tiktok-techjam")

    url = s3util.get_url(s3_file_path, "tiktok-techjam")

    task_id = str(uuid.uuid4())

    
    db = app.get_db()
    await db.execute(
        f"""
        INSERT INTO tasks(id, prompt, output_url, source_url) VALUES
        (:id, :prompt, :output_url, :source_url)
        """,
        {
            "id": task_id,
            "prompt": json.dumps(prompt),
            "output_url": "",
            "source_url": url
        }
    )

    # TODO: Send to worker (celery)

    return task_id