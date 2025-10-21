# app/services/db.py
from sqlmodel import SQLModel, create_engine
from pathlib import Path
import os

DEFAULT_DB_PATH = Path("app/expense.db")
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("sqlite:///"):
        _path = DATABASE_URL.replace("sqlite:///", "")
        DB_PATH = Path(_path)
    else:
        DB_PATH = DEFAULT_DB_PATH
else:
    DB_PATH = DEFAULT_DB_PATH

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=True) 

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
