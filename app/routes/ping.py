from fastapi import APIRouter, Depends
from app.models.user import User
from app.controller.ping.hello_user import hello_user_controller

router = APIRouter(prefix="/ping", tags=["Ping"])

@router.get("/")
async def hello_user(

): 
    """
    Hello world! 
    """
    return hello_user_controller()
