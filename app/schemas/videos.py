from pydantic import BaseModel
from typing import Optional

class VideoResponse(BaseModel):
    id: str
    caption: Optional[str] = None
    music: Optional[str] = None
    videoUrl: str
    name: str

