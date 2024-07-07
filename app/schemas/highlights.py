from pydantic import BaseModel

class HighlightsResultResponse(BaseModel):
    id: str
    output_url: str

class HighlightsPostRequest(BaseModel):
    video_url: str
    music: str
    caption: str