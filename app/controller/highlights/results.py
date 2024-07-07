from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.schemas.highlights import HighlightsResultResponse
from app.database.db import get_db

db = get_db()

async def get_results_controller(task_id: str) -> JSONResponse:
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id is required")

    query = """
    SELECT id, output_url
    FROM tasks WHERE id = :task_id
    """
    
    try:
        await db.connect()
        result = await db.fetch_one(query=query, values={"task_id": task_id})
        await db.disconnect()

        return JSONResponse(content={"id": result["id"], "output_url": result["output_url"]})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))
    


async def edit_video_controller(task_id: str, edit_request: HighlightsResultResponse):
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id is required")
    
    # query = """
    # INSERT VALUES INTO video (videoUrl, caption, music)

    # """
    
    # try:
    #     await db.connect()
    #     await db.execute(query=query, values={"task_id": task_id, "caption": edit_request.caption, "music": edit_request.music})
    #     await db.disconnect()
    #     return "Video metadata updated"
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="Internal server error: " + str(e))
