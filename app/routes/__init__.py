from fastapi import APIRouter
from .ping import router as ping_router

def register_routes(router: APIRouter):
    router.include_router(ping_router)