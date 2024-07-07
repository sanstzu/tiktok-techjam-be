from fastapi import APIRouter, UploadFile, Request
from app.controller.highlights.results import get_results_controller, post_video_controller
from app.controller.highlights.upload import upload_controller 
from app.controller.highlights.status import get_status_controller
from typing import List
from app.schemas.highlights import HighlightsResultResponse, HighlightsPostRequest

router = APIRouter(prefix="/highlights", tags=["highlights"])

@router.post("/upload", response_model=str)
async def upload_video(
    request: Request,
    file: UploadFile,
    prompt: List[str]
):
    """
    Starts task to highlight a video
    """
    user_id = request.state.user_id
    return await upload_controller(file.file, prompt, user_id)

@router.get("/{task_id}/results", response_model=HighlightsResultResponse)
async def get_video_result(task_id: str): 
    """
    Get generated video from task ID
    """
    return await get_results_controller(task_id)

@router.post("/{task_id}/post", response_model=str)
async def post_video(
    request: Request,  
    post_request: HighlightsPostRequest,
    task_id: str
): 
    """
    Post a video's metadata
    """
    user_id = request.state.user_id
    return await post_video_controller(post_request, task_id, user_id)


@router.get("/{id}/status", response_model=str)
def video_status(
    id: str
): 
    """
    Get highlight status, to check progress
    """
    return get_status_controller(id)
