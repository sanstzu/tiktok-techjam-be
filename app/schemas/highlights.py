from pydantic import BaseModel

class HighlightsResultResponse(BaseModel):
    id: str
    output_url: str
