import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy import text  
from app.models.model import Expense
import app.services.expenses_service as service

# Setup: Create in-memory test engine
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, echo=False)

# Override the real engine in the service module
@pytest.fixture(scope="module", autouse=True)
def override_engine():
    SQLModel.metadata.create_all(test_engine)
    service.engine = test_engine  
    yield

# Clear DB before each test
@pytest.fixture(autouse=True)
def clean_db():
    with Session(test_engine) as session:
        session.exec(text("DELETE FROM expense"))  
        session.commit()
    yield

# Test: Add Expense
def test_add_expense():
    service.add_expense(100.50, "food", "2025-10-21", "Lunch")

    with Session(test_engine) as session:
        expenses = session.exec(select(Expense)).all()
        assert len(expenses) == 1
        assert expenses[0].amount == 100.50
        assert expenses[0].category == "food"
        assert expenses[0].description == "Lunch"

# Test: Get Summary
def test_get_summary():
    service.add_expense(50, "food", "2025-10-21", "Breakfast")
    service.add_expense(150, "transport", "2025-10-21", "Taxi")
    service.add_expense(100, "food", "2025-10-22", "Lunch")

    summary = service.get_summary()

    assert summary["total"] == 300
    assert summary["by_category"]["food"] == 150
    assert summary["by_category"]["transport"] == 150

    summary_food = service.get_summary(category="food")
    assert summary_food["total"] == 150
    assert summary_food["by_category"]["food"] == 150
