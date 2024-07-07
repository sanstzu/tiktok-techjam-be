from fastapi import APIRouter, Request
from app.controller.videos.videos import get_user_videos_controller, get_fyp_videos_controller
from app.schemas.videos import VideoResponse
from typing import List

router = APIRouter(prefix="/videos", tags=["Video"])

@router.get("/fyp", response_model=List[VideoResponse])
async def video_download():
    """
    Fetch FYP videos
    """
    return get_fyp_videos_controller()

@router.get("/", response_model=List[VideoResponse])
async def video_download(request: Request):
    """
    Fetch all videos uploaded by a user
    """
    user_id = request.state.user_id
    return await get_user_videos_controller(user_id)
