from typing import TypedDict


class TenantData(TypedDict):
    full_name: str
    full_address: str
    vat_number: str | None


class ProductData(TypedDict):
    material: str
    remarks: str | None
    damage_cost: int
