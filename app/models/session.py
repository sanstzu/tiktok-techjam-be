from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Session(BaseModel):
    sessionToken: str = Field(..., primary_key=True)
    userId: str = Field(..., foreign_key="User.id", onDelete="cascade")
    expires: datetime = Field(..., mode="date")



