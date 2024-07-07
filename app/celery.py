import os
import time
from celery import Celery
import dotenv
import os
from asgiref.sync import async_to_sync
from typing import List
import tempfile
import app.utils.s3 as utils
import ML.main as ml_main
import uuid
import app.database.db as db

dotenv.load_dotenv()

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

def init_db():
    async_to_sync(db.connect_db)()


@celery.task(name="create_task")
def create_task(prompt: str):
    time.sleep(10)
    return "Your prompt is: " + prompt

@celery.task(name="generate_highlights")
def generate_highlights(task_id: str, s3_path: str, prompt: List[str]):
    tmp_file = os.path.join("tmp", f"{str(uuid.uuid4())}.mp4")
    utils.download_from_bucket(tmp_file, s3_path, "tiktok-techjam")
    output_file = ml_main.main(tmp_file, prompt)

    utils.upload_to_bucket(output_file, f"highlights/{os.path.basename(output_file)}", "tiktok-techjam")

    url = utils.get_url(f"highlights/{os.path.basename(output_file)}", "tiktok-techjam")

    # update to db
    async_to_sync(db.get_db().execute)(
        """
        UPDATE tasks
        SET output_url = :output_url
        WHERE id = :id
        """,
        {"output_url": url, "id": task_id}
    )




    


