from app.models.user import User
from pydantic import BaseModel
import datetime
from app.models.videos import VideoModel
from typing import List

sample_video_1: VideoModel = VideoModel(
    id="1",
    username="user1",
    caption="caption1",
    music="Adele - Hello",
    videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-1.mp4",
    userId="user1"
)

sample_video_2: VideoModel = VideoModel(
    id="2",
    username="user1",
    caption="English or Spanish",
    music=None,
    videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-2.mp4",
    userId="user1"
)

sample_video_3: VideoModel = VideoModel(
    id="3",
    username="user2",
    caption="Spelling Bee Contest Championship",
    music=None,
    videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-3.mp4",
    userId="user2"
)
    

async def get_videos_controller(user: str):
    if user is None:
        # TODO: query all videos from the database
        return [sample_video_1, sample_video_2, sample_video_3]
    else:
        # TODO: query all videos for a user id
        return [sample_video_1, sample_video_2]
