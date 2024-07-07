from app.models.user import User
from pydantic import BaseModel
import datetime

class ResponseModel(BaseModel):
    message: str
    date: str

def hello_user_controller():
    return "pong"