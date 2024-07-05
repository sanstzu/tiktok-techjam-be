from pydantic import BaseModel
from typing import Optional

class VideoModel(BaseModel):
    id: str
    username: str
    caption: Optional[str] = None
    music: Optional[str] = None
    videoUrl: str
    userId: str