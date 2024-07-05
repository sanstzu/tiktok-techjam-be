from fastapi import FastAPI
from app.routes import register_routes
import time

# How do you name the file such that a .py in routes
# can be imported as routes
# Answs
server = FastAPI(title="API", version="0.1.0")

# debug
server.ts = 0
def get_timestamp_percentage():
    if time.time() - server.ts > 20:
        server.ts = time.time()

    return min((time.time() - server.ts) * 10, 100.0)


register_routes(server)