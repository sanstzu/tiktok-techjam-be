import os
import time
from celery import Celery
import dotenv
import os

dotenv.load_dotenv()

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

@celery.task(name="highlight_video")
def create_highlight_video_task(prompt: str):
    time.sleep(10)
    return "Your prompt is: " + prompt


