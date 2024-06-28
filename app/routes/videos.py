from fastapi import APIRouter, UploadFile, HTTPException
from app.controller.videos.upload import upload_controller

router = APIRouter(prefix="/videos", tags=["Video"])

@router.post("/upload")
async def video_upload(
    file: UploadFile 
): 
    """
    Upload a video file
    """
    if file.content_type != "video/mp4":
        raise HTTPException(400, detail="Invalid video type")
    return await upload_controller(file.file)
