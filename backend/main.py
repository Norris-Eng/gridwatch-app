from fastapi import FastAPI
import os

app = FastAPI()

# Read environment variables
db_host = os.getenv("DB_HOST", "db_host_not_set")
db_user = os.getenv("DB_USER", "db_user_not_set")
db_name = os.getenv("DB_NAME", "db_name_not_set")


@app.get("/")
def read_root():
    """
    Root endpoint that confirms the API is running
    and checks if it has successfully loaded database credentials.
    """
    return {
        "message": "GridWatch API is running.",
        "database_connection": {
            "host": db_host,
            "user": db_user,
            "database": db_name
        }
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint for the container.
    """
    return {"status": "ok"}
