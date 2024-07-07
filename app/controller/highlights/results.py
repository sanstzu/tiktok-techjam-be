from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.schemas.highlights import HighlightsPostRequest
from app.database.db import get_db
import uuid

db = get_db()

async def get_results_controller(task_id: str) -> JSONResponse:
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id is required")

    query = """
    SELECT id, output_url
    FROM tasks WHERE id = :task_id
    """
    
    try:
        result = await db.fetch_one(query=query, values={"task_id": task_id})

        return JSONResponse(content={"id": result["id"], "output_url": result["output_url"]})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))
    


async def post_video_controller(post_request: HighlightsPostRequest, user_id: str) -> str:
    query = """
    INSERT INTO video (id, "videoUrl", caption, music, "userId")
    VALUES (:id, :video_url, :caption, :music, :user_id)
    """
    try:
        await db.execute(query=query, values={"id": str(uuid.uuid4()), "video_url": post_request.video_url, "caption": post_request.caption, "music": post_request.music, "user_id": user_id})

        return "Video metadata updated"
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))
   