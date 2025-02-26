from typing import TypedDict


class ExpenseReportRecipientData(TypedDict):
    name: str
    surname: str
    email_address: str
    account_number: str
    date: str


class ExpenseReportData(TypedDict):
    journal_entry: str
    description: str
    cost_or_km: int
