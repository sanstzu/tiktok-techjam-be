from fastapi import APIRouter
from .ping import router as ping_router
from .videos import router as videos_router

def register_routes(router: APIRouter):
    router.include_router(ping_router)
    router.include_router(videos_router)