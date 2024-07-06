from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import uuid

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4)
    name: Optional[str] = None
    email: EmailStr
    emailVerified: Optional[datetime] = None
    image: Optional[str] = None