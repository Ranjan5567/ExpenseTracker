# app/models/model.py
from sqlmodel import SQLModel, Field
from typing import Optional

class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    category: str
    date: str
    description: str
