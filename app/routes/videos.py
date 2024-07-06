from fastapi import APIRouter, Request
from app.controller.videos.videos import get_user_videos_controller
from app.schemas.videos import VideoResponse
from typing import List

router = APIRouter(prefix="/videos", tags=["Video"])

@router.get("/fyp", response_model=List[VideoResponse])
async def video_download():
    """
    Fetch FYP videos
    """

    sample_video_1 = VideoResponse(
        id="testid-1",
        caption="what's cooler than a hot chocolate?",
        music="Adele - Hello",
        videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-1.mp4",
        name="RickyGlow"
    )

    sample_video_2 = VideoResponse(
        id="testid-2",
        caption="English or Spanish",
        music=None,
        videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-2.mp4",
        name="Martinez Twins"
    )

    sample_video_3 = VideoResponse(
        id="testid-3",
        caption="Spelling Bee Contest Championship",
        music="original audio - Masuk Pak Eko",
        videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-3.mp4",
        name="Lius Lasahido"
    )

    return [sample_video_1, sample_video_2, sample_video_3]

@router.get("/", response_model=List[VideoResponse])
async def video_download(request: Request):
    """
    Fetch all videos uploaded by a user
    """
    user_id = request.state.user_id
    return await get_user_videos_controller(user_id)
