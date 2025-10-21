from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import expenses
from app.services.db import init_db

# Initialize database
init_db()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routes
app.include_router(expenses.router)
