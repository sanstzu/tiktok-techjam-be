from fastapi import APIRouter, UploadFile, HTTPException
from app.controller.videos.videos import get_videos_controller
from app.models.videos import VideoModel
from typing import List

router = APIRouter(prefix="/videos", tags=["Video"])

@router.get("/", response_model=List[VideoModel])
async def video_download(
    user: str | None = None
):
    """
    Download a video file
    """
    return get_videos_controller(user)
