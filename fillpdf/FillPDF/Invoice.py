from typing import List

from pypdf import PdfReader, PdfWriter

from fillpdf.TypedDicts.Invoice import InvoiceRecipientData, InvoiceProductsData


class Invoice:
    def __init__(self) -> None:
        self.max_amount = None

    async def change_max_amount(self, new_max_amount) -> None:
        self.max_amount = new_max_amount

    async def fill(
        self,
        reference_number: int,
        date: str,
        days: int,
        recipient_data: InvoiceRecipientData,
        products: List[InvoiceProductsData],
    ) -> None:
        """
        Fills the template Invoice.pdf with the given information
        :param days: The amount of days the recipient has to pay
        :param reference_number: Reference number of the invoice
        :param date: Date the invoice is issued
        :param recipient_data: Data of the recipient of the invoice
        :param products: List of products that are sold
        """
        # Get standard variables out of the pdf
        reader = PdfReader("fillpdf/Templates/Invoice.pdf", strict=False)
        writer = PdfWriter()
        writer.append(reader)

        writer.update_page_form_field_values(
            writer.pages[0],
            {
                "Volgnummer": str(reference_number),
                "Factuurdatum": date,
                "Betaaldagen": str(days),
                "Begunstigde": recipient_data.get("beneficiary"),
                "Departement": recipient_data.get("department") or "",
                "Adres1": recipient_data.get("street_and_house_number"),
                "Adres2": recipient_data.get("municipality_and_zip_code"),
                "BTW": recipient_data.get("vat_number") or "",
                "Ordernummer": recipient_data.get("order_number") or "",
            },
            auto_regenerate=False,
        )

        if len(products) > self.max_amount:
            raise Exception(
                f"Max allowed products is {self.max_amount}, but received {len(products)}."
            )
        i = 1
        total_inclusive = 0
        total_exclusive = 0

        for product in products:
            total_product = product.get("cost") * product.get("amount")
            total_exclusive += total_product
            total_inclusive += total_product * (1 + product.get("vat_amount") / 100)

            writer.update_page_form_field_values(
                writer.pages[0],
                {
                    "Boekhoudpost" + str(i): str(product.get("journal_entry")),
                    "Beschrijving" + str(i): product.get("description"),
                    "Prijs" + str(i): str(product.get("cost")),
                    "Aantal" + str(i): str(product.get("amount")),
                    "BTW" + str(i): str(product.get("vat_amount")),
                    "Totaal" + str(i): str(total_product / 100),
                },
                auto_regenerate=False,
            )
            i += 1

        writer.update_page_form_field_values(
            writer.pages[0],
            {
                "TotaalExclusief": str(total_exclusive / 100),
                "TotaalInclusief": str(total_inclusive / 100),
            },
            auto_regenerate=False,
        )
