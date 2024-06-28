from app.models.user import User
from pydantic import BaseModel
import datetime

class ResponseModel(BaseModel):
    message: str
    date: str

async def hello_user_controller(email: str, password: str):
    return {
        "message": f"Hello, {email}!",
        "date": datetime.datetime.now().isoformat()
    }