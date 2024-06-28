from fastapi import APIRouter, UploadFile, HTTPException
from app.controller.highlights.results import get_results_controller
from app.controller.highlights.start import start_highlight_task_controller
from app.controller.highlights.status import get_status_controller

router = APIRouter(prefix="/highlights", tags=["highlights"])

@router.get("/start")
def video_download(
    video_id: str,
    prompt: str
):
    """
    Starts task to highlight a video
    """
    return start_highlight_task_controller(video_id, prompt)

@router.get("/{highlight_id}/results")
def video_upload(
    highlight_id: str
): 
    """
    Get highlight results
    """

    return get_results_controller(highlight_id)


@router.get("/{highlight_id}/status")
def video_upload(
    highlight_id: str
): 
    """
    Get highlight status, to check progress
    """

    return get_status_controller(highlight_id)
