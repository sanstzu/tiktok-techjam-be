from tempfile import SpooledTemporaryFile, mkstemp
import app.main as app
import app.utils.s3 as s3util
import time
from fastapi import HTTPException

# For debugging purposes

zero_percent_timestamp = 0

def __get_debug_percentage():
    return app.get_timestamp_percentage()

async def get_status_controller(id: str):
    # get from tasks table, return 0 if  output_url is null
    db = app.get_db()
    query = """
    SELECT output_url FROM tasks WHERE id = :id
    """
    try:
        result = await db.fetch_one(query=query, values={"id": id})
        if result is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if result["output_url"] is None:
            return 0
        return 100
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))