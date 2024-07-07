from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.controller.highlights.results import get_results_controller, edit_video_controller
from app.controller.highlights.upload import upload_controller 
from app.controller.highlights.status import get_status_controller
from typing import List
from app.schemas.highlights import HighlightsResultResponse, HighlightsEditRequest

router = APIRouter(prefix="/highlights", tags=["highlights"])

@router.post("/upload", response_model=str)
async def upload_video(
    file: UploadFile,
    prompt: List[str]
):
    """
    Starts task to highlight a video
    """
    return await upload_controller(file.file, prompt)

@router.get("/{task_id}/results", response_model=HighlightsResultResponse)
async def get_video_result(task_id: str): 
    """
    Get generated video from task ID
    """
    return await get_results_controller(task_id)

@router.post("/{task_id}/edit", response_model=str)
async def edit_video(
    task_id: str,
    edit_request: HighlightsEditRequest
): 
    """
    Edit a video's metadata
    """
    return await edit_video_controller(task_id, edit_request)


@router.get("/{id}/status", response_model=str)
def video_status(
    id: str
): 
    """
    Get highlight status, to check progress
    """

    return get_status_controller(id)
