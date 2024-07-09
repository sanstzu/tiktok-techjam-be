from pydantic import BaseModel
from typing import Optional

class HighlightsResultResponse(BaseModel):
    id: str
    output_url: str

class HighlightsPostRequest(BaseModel):
    video_url: str
    music: Optional[str] = None
    caption: Optional[str] = None