from tempfile import SpooledTemporaryFile, mkstemp
import os
import app.utils.s3 as s3util
import uuid


def find_highlight_controller(video_id: str, prompt: str):
    
    highlight_id = uuid.uuid4()

    # TODO: Add video_id, prompt to database
    # Possible schema highlight(id, video_id, prompt, created_at, celery_task_id)

    # TODO: Send to worker

    return highlight_id