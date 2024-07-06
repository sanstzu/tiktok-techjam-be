from app.schemas.videos import VideoResponse
from typing import List
from fastapi import HTTPException
from app.database.db import get_db

db = get_db()

async def get_user_videos_controller(user_id: str) -> List[VideoResponse]:
    query = """
    SELECT video.id, video.caption, video.music, video."videoUrl", "user"."name"
    FROM video
    JOIN "user" ON video."userId" = "user".id
    WHERE video."userId" = :user_id
    LIMIT 50
    """
    try:
        await db.connect()
        result = await db.fetch_all(query=query, values={"user_id": user_id})
        await db.disconnect()
        videos = [VideoResponse(**video) for video in result]
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))