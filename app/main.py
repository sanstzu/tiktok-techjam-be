from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .celery import create_task
from app.database.db import connect_db, disconnect_db, get_db
from app.routes import register_routes
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting server")
    await connect_db()
    yield
    print("Stopping server")
    await disconnect_db()

server = FastAPI(title="API", version="0.1.0", lifespan=lifespan)

# debug
server.ts = 0
def get_timestamp_percentage():
    if time.time() - server.ts > 20:
        server.ts = time.time()

    return min((time.time() - server.ts) * 10, 100.0)

db = get_db()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_session_user(request: Request, token: str = Depends(oauth2_scheme)):
    session_token = token
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token not found")

    query = """
    SELECT "userId" FROM session WHERE "sessionToken" = :session_token
    """
    
    try:
        result = await db.fetch_one(query=query, values={"session_token": session_token})
        if result is None:
            raise HTTPException(status_code=401, detail="Session not found")
        return result["userId"]
    except Exception as e:
        err = str(e)
        print("ERROR: ", err)
        raise HTTPException(status_code=500, detail=f"Internal server error: {err}")

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
        return JSONResponse(status_code=e.status_code, content=e.detail)
    request.state.user_id = user_id
    response = await call_next(request)
    return response

allowed_origins = [
    "https://tiktok-highlights.vercel.app",
    "*",
]

server.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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
  
