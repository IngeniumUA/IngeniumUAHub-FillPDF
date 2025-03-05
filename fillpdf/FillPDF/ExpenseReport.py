import io
from typing import List

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from fillpdf.TypedDicts.ExpenseReport import (
    ExpenseReportData,
    ExpenseReportRecipientData,
)


class ExpenseReport:
    def __init__(self) -> None:
        self.travel_expense_reimbursement: int = 0
        self.max_amount: int = 0

    async def _resize_image_to_a4(self, image, page_width, page_height):
        """

        :param image:
        :param page_width:
        :param page_height:
        :return:
        """
        image_width, image_height = image.size
        if image_width > page_width or image_height > page_height:
            if image_width > image_height:
                ratio = page_width / image_width
            else:
                ratio = page_height / image_height

            image_width *= ratio
            image_height *= ratio

        return image_width, image_height

    async def change_max_amount(self, new_max_amount) -> None:
        """

        :param new_max_amount:
        """
        self.max_amount = new_max_amount

    async def change_travel_expenses_reimbursement(
        self, new_travel_expenses_reimbursement
    ) -> None:
        """

        :param new_travel_expenses_reimbursement:
        """
        self.travel_expense_reimbursement = new_travel_expenses_reimbursement

    async def fill(
        self,
        reference_number: int,
        recipient_data: ExpenseReportRecipientData,
        expenses: List[ExpenseReportData],
        date: str,
        template: bytes,
        attachments: List[bytes] = None,
    ) -> bytes | None:
        """

        :param template:
        :param reference_number:
        :param recipient_data:
        :param expenses:
        :param date:
        :param attachments:
        """
        # Get standard variables out of the pdf
        byte_stream = io.BytesIO(template)
        reader = PdfReader(byte_stream, strict=False)
        writer = PdfWriter()
        writer.append(reader)

        writer.update_page_form_field_values(
            writer.pages[0],
            {
                "Vervoersonkosten": str(self.travel_expense_reimbursement / 100),
                "Volgnummer": str(reference_number),
                "DatumVoldaan": date,
                " Voornaam": recipient_data.get("name"),
                "Naam": recipient_data.get("surname"),
                "Email": recipient_data.get("email_address"),
                "Rekeningnummer": recipient_data.get("account_number"),
                "DatumGemaakt": recipient_data.get("date"),
            },
            auto_regenerate=False,
        )

        if len(expenses) > self.max_amount:
            raise Exception(
                f"Max allowed expenses is {self.max_amount}, but received {len(expenses)}."
            )

        i = 1
        total = 0
        for expense in expenses:
            temporary_price = expense.get("cost_or_km")

            if expense.get("journal_entry") == "615000":
                temporary_price *= self.travel_expense_reimbursement

            writer.update_page_form_field_values(
                writer.pages[0],
                {
                    "Boekhoudpost" + str(i): str(expense.get("journal_entry")),
                    "Beschrijving" + str(i): expense.get("description"),
                    "Prijs" + str(i): str(temporary_price / 100),
                },
                auto_regenerate=False,
            )

            i += 1
            total += temporary_price

            writer.update_page_form_field_values(
                writer.pages[0],
                {"Totaal": str(total / 100)},
                auto_regenerate=False,
            )

        if attachments:
            for attachment in attachments:
                byte_stream = io.BytesIO(attachment)
                if byte_stream.read(len(b"%PDF-")) == b"%PDF-":
                    writer.append(fileobj=byte_stream)
                else:
                    image = Image.open(attachment)
                    pdf_buffer = io.BytesIO()
                    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
                    page_width, page_height = A4
                    image_width, image_height = self._resize_image_to_a4(
                        image, page_width, page_height
                    )

                    # (0,0) is lower left corner
                    x, y = 0, page_height - image_height

                    pdf.drawInlineImage(
                        image=image, x=x, y=y, width=image_width, height=image_height
                    )
                    pdf.save()
                    pdf_buffer.seek(0)
                    writer.append(fileobj=pdf_buffer)
                    pdf_buffer.close()

        # Write final combined PDF to buffer and return bytes
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        return output_buffer.getvalue()
