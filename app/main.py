from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from databases import Database
import dotenv
import os

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_session_user(request: Request, token: str = Depends(oauth2_scheme)):
    session_token = token
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token not found")

    query = """
    SELECT "userId" FROM session WHERE "sessionToken" = :session_token
    """
    
    try:
        await database.connect()
        result = await database.fetch_one(query=query, values={"session_token": session_token})
        await database.disconnect()
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

@server.middleware("http")
async def add_session_user(request: Request, call_next):
    user_id = None
    try:
        authorization: str = request.headers.get("Authorization")
        if authorization:
            scheme, _, token = authorization.partition(' ')
            if scheme.lower() == 'bearer':
                user_id = await get_session_user(request, token)
    except HTTPException:
        pass
    request.state.user_id = user_id
    response = await call_next(request)
    return response

register_routes(server)

@server.get("/example")
async def example_route(request: Request):
    if not request.state.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "This is a protected route", "user_id": request.state.user_id}