from fastapi import APIRouter, Form, Request, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from app.services.expenses_service import (
    add_expense,
    get_all_expenses,
    get_summary,
    get_filter_options,
)
import io
import csv

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Home page: form + table
@router.get("/")
def home(request: Request):
    expenses = get_all_expenses()
    return templates.TemplateResponse("index.html", {"request": request, "expenses": expenses})

# Add new expense
@router.post("/add_expense")
def add_expense_route(
    amount: float = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    description: str = Form(...)
):
    category = category.strip().lower()
    add_expense(amount, category, date, description)
    return RedirectResponse(url="/", status_code=303)

# Summary page with filters
@router.get("/summary")
def summary(
    request: Request,
    year: str | None = Query(None),
    month: str | None = Query(None),
    day: str | None = Query(None),
    category: str | None = Query(None),
):
    expenses = get_all_expenses()
    summary_data = get_summary(year, month, day, category)
    display_summary = {cat.title(): amt for cat, amt in summary_data["by_category"].items()}
    summary_data["by_category"] = display_summary
    
    filter_options = get_filter_options()

    return templates.TemplateResponse(
        "summary.html",
        {
            "request": request,
            "summary": summary_data,
            "years": filter_options["years"],
            "months": filter_options["months"],
            "days": filter_options["days"],
            "categories": filter_options["categories"],
            "expenses": expenses,
            "selected_year": year,
            "selected_month": month,
            "selected_day": day,
            "selected_category": category,
        },
    )

# Export all expenses as CSV
@router.get("/export")
def export_expenses():
    expenses = get_all_expenses()

    # Create CSV in-memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Amount", "Category", "Date", "Description"])

    for exp in expenses:
        writer.writerow([
            exp["id"],
            exp["amount"],
            exp["category"].title(),
            exp["date"],
            exp["description"]
        ])

    output.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=expenses.csv"
    }
    return StreamingResponse(output, media_type="text/csv", headers=headers)