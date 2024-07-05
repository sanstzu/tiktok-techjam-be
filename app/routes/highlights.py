from fastapi import APIRouter, UploadFile, HTTPException
from app.controller.highlights.results import get_results_controller
from app.controller.highlights.upload import upload_controller 
from app.controller.highlights.status import get_status_controller
from typing import List
from app.models.videos import VideoModel

router = APIRouter(prefix="/highlights", tags=["highlights"])

@router.post("/upload", response_model=str)
def video_download(
    file: UploadFile,
    prompt: List[str]
):
    """
    Starts task to highlight a video
    """
    return upload_controller(file, prompt)

@router.get("/{id}/results", response_model=VideoModel)
def video_upload(
    id: str
): 
    """
    Get highlight results
    """

    return get_results_controller(id)


@router.get("/{id}/status", response_model=float)
def video_upload(
    id: str
): 
    """
    Get highlight status, to check progress
    """

    return get_status_controller(id)
