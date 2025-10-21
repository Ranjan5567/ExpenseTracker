# app/services/expenses_service.py
from sqlmodel import Session, select
from app.models.model import Expense
from app.services.db import engine
from sqlalchemy import text

# Add new expense
def add_expense(amount, category, date, description):
    category = category.strip().lower()
    expense = Expense(amount=amount, category=category, date=date, description=description)
    with Session(engine) as session:
        session.add(expense)
        session.commit()

# Fetch all expenses
def get_all_expenses():
    with Session(engine) as session:
        expenses = session.exec(select(Expense).order_by(Expense.date.desc())).all()
        return [
            {
                "id": exp.id,
                "amount": exp.amount,
                "category": exp.category.title(),
                "date": exp.date,
                "description": exp.description
            }
            for exp in expenses
        ]

def get_filter_options():
    with Session(engine) as session:
        years = session.exec(text("SELECT DISTINCT strftime('%Y', date) as year FROM expense ORDER BY year")).all()
        months = session.exec(text("SELECT DISTINCT strftime('%m', date) as month FROM expense ORDER BY month")).all()
        days = session.exec(text("SELECT DISTINCT strftime('%d', date) as day FROM expense ORDER BY day")).all()
        categories = session.exec(text("SELECT DISTINCT category FROM expense ORDER BY category")).all()

        years = [y[0] for y in years if y[0]]
        months = [m[0] for m in months if m[0]]
        days = [d[0] for d in days if d[0]]
        categories = [c[0].title() for c in categories if c[0]]

        return {
            "years": years,
            "months": months,
            "days": days,
            "categories": categories,
        }

def get_summary(year=None, month=None, day=None, category=None):
    from sqlalchemy import func, and_
    with Session(engine) as session:
        filters = []
        if year:
            filters.append(func.strftime('%Y', Expense.date) == year)
        if month:
            filters.append(func.strftime('%m', Expense.date) == month)
        if day:
            filters.append(func.strftime('%d', Expense.date) == day)
        if category:
            filters.append(func.lower(Expense.category) == category.lower())

        query = session.query(Expense.category, func.sum(Expense.amount).label("total"))

        if filters:
            query = query.filter(and_(*filters))

        query = query.group_by(Expense.category)
        results = query.all()

        by_category = {cat: total for cat, total in results}
        total = sum(by_category.values()) if by_category else 0

        return {"total": total, "by_category": by_category}
