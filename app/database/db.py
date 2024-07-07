from databases import Database
import dotenv
import os

dotenv.load_dotenv()

database = Database(os.getenv("POSTGRES_URL"))

async def connect_db():
    await database.connect()

async def disconnect_db():
    await database.disconnect()

def get_db():
    return database