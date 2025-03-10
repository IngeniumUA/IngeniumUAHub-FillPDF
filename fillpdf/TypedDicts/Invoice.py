from typing import TypedDict


class InvoiceRecipientData(TypedDict):
    beneficiary: str
    department: str | None
    street_and_house_number: str
    municipality_and_zip_code: str
    vat_number: str | None
    order_number: str | None


class InvoiceProductsData(TypedDict):
    journal_entry: int
    description: str
    cost: int
    amount: int
    vat_amount: int
