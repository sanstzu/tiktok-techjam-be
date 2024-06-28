from fastapi import APIRouter, UploadFile, HTTPException
from app.controller.videos.upload import upload_controller
from app.controller.videos.download import get_video_controller
from app.controller.videos.thumbnail import get_thumbnail_controller

router = APIRouter(prefix="/videos", tags=["Video"])

@router.post("/upload")
def video_upload(
    file: UploadFile 
): 
    """
    Upload a video file
    """
    if file.content_type != "video/mp4":
        raise HTTPException(400, detail="Invalid video type")
    return upload_controller(file.file)

@router.get("/{video_id}/download")
def video_download(
    video_id: str
):
    """
    Download a video file
    """
    return get_video_controller(video_id)

@router.get("/{video_id}/thumbnail")
def video_thumbnail(
    video_id: str
):
    """
    Download a video thumbnail
    """
    return get_thumbnail_controller(video_id)
