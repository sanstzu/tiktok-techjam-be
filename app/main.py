from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from databases import Database
from .celery import create_task
import dotenv
import os
import asyncio

dotenv.load_dotenv()

from app.routes import register_routes
import time

server = FastAPI(title="API", version="0.1.0")

# debug
server.ts = 0
def get_timestamp_percentage():
    if time.time() - server.ts > 20:
        server.ts = time.time()

    return min((time.time() - server.ts) * 10, 100.0)

database = Database(os.getenv("POSTGRES_URL"))

def get_db():
    return database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_session_user(request: Request, token: str = Depends(oauth2_scheme)):
    session_token = token
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token not found")

    query = """
    SELECT "userId" FROM session WHERE "sessionToken" = :session_token
    """
    
    try:
        
        db = get_db()
        await db.connect()
        result = await db.fetch_one(query=query, values={"session_token": session_token})
        await db.disconnect()
        if result is None:
            raise HTTPException(status_code=401, detail="Session not found")
        return result["userId"]
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

original_openapi = server.openapi

def custom_openapi():
    if server.openapi_schema:
        return server.openapi_schema
    
    openapi_schema = original_openapi()
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    server.openapi_schema = openapi_schema
    return server.openapi_schema

server.openapi = custom_openapi

EXCLUDE_PATHS = ["/docs", "/openapi.json"]

@server.middleware("http")
async def add_session_user(request: Request, call_next):
    if request.url.path in EXCLUDE_PATHS:
        return await call_next(request)

    user_id = None
    try:
        authorization: str = request.headers.get("Authorization")
        if authorization:
            scheme, _, token = authorization.partition(' ')
            if scheme.lower() == 'bearer':
                user_id = await get_session_user(request, token)
            else:
                return JSONResponse(status_code=401, content="Invalid authorization scheme or token")
        else:
            return JSONResponse(status_code=401, content="Authorization header not found")
    except HTTPException as e:
        raise JSONResponse(status_code=e.status_code, content=e.detail)
    request.state.user_id = user_id
    response = await call_next(request)
    return response

@server.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@server.on_event("startup")
async def startup():
    await database.connect()

@server.get("/example")
async def example_route(request: Request):
    if not request.state.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "This is a protected route", "user_id": request.state.user_id}

@server.post("/example/task")
def run_task(request: Request):
    task = create_task.delay(prompt = "Hello, world!")
    return JSONResponse({"Response": task.get()})
  
register_routes(server)
