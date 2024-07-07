from app.schemas.videos import VideoResponse
from typing import List
from fastapi import HTTPException
from app.database.db import get_db

db = get_db()

def get_fyp_videos_controller() -> List[VideoResponse]:
    sample_video_1 = VideoResponse(
        id="testid-1",
        caption="what's cooler than a hot chocolate?",
        music="Adele - Hello",
        videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-1.mp4",
        name="RickyGlow"
    )

    sample_video_2 = VideoResponse(
        id="testid-2",
        caption="English or Spanish",
        music=None,
        videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-2.mp4",
        name="Martinez Twins"
    )

    sample_video_3 = VideoResponse(
        id="testid-3",
        caption="Spelling Bee Contest Championship",
        music="original audio - Masuk Pak Eko",
        videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-3.mp4",
        name="Lius Lasahido"
    )

    return [sample_video_1, sample_video_2, sample_video_3]


async def get_user_videos_controller(user_id: str) -> List[VideoResponse]:
    query = """
    SELECT video.id, video.caption, video.music, video."videoUrl", "user"."name"
    FROM video
    JOIN "user" ON video."userId" = "user".id
    WHERE video."userId" = :user_id
    ORDER BY video."postTime" DESC
    LIMIT 50
    """
    try:
        result = await db.fetch_all(query=query, values={"user_id": user_id})
        videos = [VideoResponse(**video) for video in result]
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))