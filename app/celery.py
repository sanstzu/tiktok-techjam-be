import os
import time
from celery import Celery, signals
import dotenv
import os
from asgiref.sync import async_to_sync
from typing import List
import tempfile
import app.utils.s3 as utils
import ML.main as ml_main
import uuid
import app.database.db as db
import asyncio
from concurrent.futures import ThreadPoolExecutor
from databases import Database


def run_async(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return loop.run_in_executor(pool, async_to_sync(func), *args, **kwargs)
    
dotenv.load_dotenv()

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

@signals.worker_init.connect
def init_worker(**kwargs):
    async_to_sync(db.connect_db)()
    print("Connected to db")
    print(db.get_db().is_connected)


@celery.task(name="create_task")
def create_task(prompt: str):
    time.sleep(10)
    return "Your prompt is: " + prompt

@celery.task(name="generate_highlights")
def generate_highlights(task_id: str, s3_path: str, prompt: List[str]):
    tmp_file = os.path.join("tmp", f"{str(uuid.uuid4())}.mp4")
    utils.download_from_bucket(tmp_file, s3_path, "tiktok-techjam")
    output_file = ""
    try:
        output_file = ml_main.main(tmp_file, prompt)
    except Exception as e:
        print(e)
        raise e

    utils.upload_to_bucket(output_file, f"highlights/{task_id}.mp4", "tiktok-techjam")

    url = utils.get_url(f"highlights/{task_id}.mp4", "tiktok-techjam")

    async def update_database():
        db = Database(os.getenv("POSTGRES_URL"))
        await db.connect()
        try:
            await db.execute(
                """
                UPDATE tasks
                SET output_url = :output_url, status = :status
                WHERE id = :id
                """,
                {"output_url": url, "id": task_id, "status": "DONE"}
            )
        finally:
            await db.disconnect()

    # Run the async database update function
    run_async(update_database)




    


