from fastapi import APIRouter, Depends
from app.models.user import User
from app.controller.ping.hello_user import hello_user_controller

router = APIRouter(prefix="/ping", tags=["Ping"])

@router.get("/")
def hello_user(
    user: str,
    password: str  
): 
    """
    Hello world! 
    """
    return hello_user_controller(user, password)
