import io
from typing import List

from pypdf import PdfReader, PdfWriter

from fillpdf.TypedDicts.RentalContract import TenantData, ProductData


class RentalContract:
    def __init__(self) -> None:
        self.max_amount: int = 0

    async def change_max_amount(self, new_max_amount) -> None:
        self.max_amount = new_max_amount

    def fill(
        self,
        reference_number: int,
        tenant_data: TenantData,
        products: List[ProductData],
        start_date: str,
        end_date: str,
        rent_cost: int,
        deposit_cost: int,
        renter: str,
        template: bytes,
    ) -> bytes:
        """

        :param template:
        :param reference_number:
        :param tenant_data:
        :param products:
        :param start_date:
        :param end_date:
        :param rent_cost:
        :param deposit_cost:
        :param renter:
        """
        byte_stream = io.BytesIO(template)
        reader = PdfReader(byte_stream, strict=False)
        writer = PdfWriter()
        writer.append(reader)
        writer.set_need_appearances_writer(True)

        writer.update_page_form_field_values(
            writer.pages[0],
            {
                "Volgnummer1": str(reference_number),
                "Volgnummer2": str(reference_number),
                "Volgnummer3": str(reference_number),
                "BTWHuurder": tenant_data.get("vat_number") or "",
                "AdresHuurder": tenant_data.get("full_address"),
                "NaamHuurder1": tenant_data.get("full_name"),
                "NaamHuurder2": tenant_data.get("full_name"),
                "NaamHuurder3": tenant_data.get("full_name"),
                "Startdatum": start_date,
                "Einddatum": end_date,
                "Huurprijs": str(rent_cost / 100),
                "Waarborg": str(deposit_cost / 100),
                "NaamIngenium1": renter,
                "NaamIngenium2": renter,
            },
            auto_regenerate=False,
        )

        if len(products) > self.max_amount:
            raise Exception(
                f"Max allowed products is {self.max_amount}, but received {len(products)}."
            )

        i = 1
        for product in products:
            writer.update_page_form_field_values(
                writer.pages[0],
                {
                    "Materiaal" + str(i): product.get("material"),
                    "Opmerkingen" + str(i): product.get("remarks") or "",
                    "Schade" + str(i): str(product.get("damage_cost") / 100)
                    + " €/stuk",
                },
                auto_regenerate=False,
            )
            i += 1

        # Write final combined PDF to buffer and return bytes
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        return output_buffer.getvalue()
