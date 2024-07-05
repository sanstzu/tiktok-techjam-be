from fastapi import HTTPException
import app.models.videos as VideoModel



def get_results_controller(task_id: str):
    sample_video_4: VideoModel = VideoModel(
        id="4",
        username="user1",
        caption="Autistic doctor saves life",
        music=None,
        videoUrl="https://tiktok-techjam.s3.ap-southeast-2.amazonaws.com/videos/sample-video-4.mp4",
        userId="user1"
    )
    if task_id is None:
        raise HTTPException(status_code=400, detail="task_id is required")
    elif task_id != "testid1":
        raise HTTPException(status_code=404, detail="task_id not found")
    else:
        return sample_video_4