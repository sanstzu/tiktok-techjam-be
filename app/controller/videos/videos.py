from app.models.user import User
from pydantic import BaseModel
import datetime
from app.models.videos import VideoModel

sample_video = [
    "https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-1.mp4"
    "https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-2.mp4"
    "https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-3.mp4"
]
    

async def get_videos_controller(user: str):
    if user is None:
        # TODO: query all videos from the database
        return sample_video
    else:
        # TODO: query all videos for a user id
        return sample_video[0:2]
