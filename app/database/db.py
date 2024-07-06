from databases import Database
import dotenv
import os

dotenv.load_dotenv()

database = Database(os.getenv("POSTGRES_URL"))

def get_db():
    return database