from fastapi import FastAPI
from app.routes import register_routes

# How do you name the file such that a .py in routes
# can be imported as routes
# Answs

app = FastAPI(title="API", version="0.1.0")

register_routes(app)