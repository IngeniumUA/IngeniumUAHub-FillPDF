from pypdf import PdfReader, PdfWriter


class ExpenseReport:
    def __init__(self) -> None:
        self.travel_expense_reimbursement = None
        self.max_amount = None
        self.boekhoudpost_vervoer = "615000"
        self.pdf_signature = b"%PDF-"

    async def change_max_amount(self, new_max_amount) -> None:
        self.max_amount = new_max_amount
        
    async def change_travel_expenses_reimbursement(self, new_travel_expenses_reimbursement) -> None:
        self.travel_expense_reimbursement = new_travel_expenses_reimbursement

    async def fill(self, reference_number: int, ):

    def filldd(self, filedata: io.BytesIO, savepath: str, volgnummer: str = None,
             gegevens: OnkostennotaGegevensDictionary = None,
             onkosten: list[OnkostennotaOnkostenDictionary] = None, betaaldatum: str = None,
             vervoersonkosten_vergoeding: Decimal = None, attachmentsdata: list[io.BytesIO] = None) -> None:
        """
        Functie die automatisch de onkostennota template invult.

        :param filedata: Data van het te bewerken bestand.
        :param savepath: Waar de onkostennota op te slaan.
        :param volgnummer: Volgnummer van de onkostennota.
        :param gegevens: Gegevens van de persoon die de onkosten gedaan heeft.
        :param onkosten: Lijst met de onkosten als dictionary. Maximaal 16.
        :param betaaldatum: Wanneer onkostennota effectief betaald wordt.
        :param vervoersonkosten_vergoeding: Hoeveel er per km vergoed wordt.
        :param attachmentsdata: Lijst van attachments data.
        """
        # Standaard variabelen, worden uit PDF gehaald
        reader = PdfReader(filedata, strict=False)
        writer = PdfWriter()
        writer.append(reader)

        # Vervoersvergoeding invullen
        if vervoersonkosten_vergoeding is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Vervoersonkosten": str(round_half_up(vervoersonkosten_vergoeding, 4))},
                auto_regenerate=False,
            )

        # Volgnummer invullen
        if volgnummer is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Volgnummer": volgnummer},
                auto_regenerate=False,
            )
        # Betaaldatum invullen
        if betaaldatum is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"DatumVoldaan": betaaldatum},
                auto_regenerate=False,
            )
        # Gegevens invullen
        if gegevens is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Voornaam": gegevens["voornaam"], "Naam": gegevens["naam"], "Email": gegevens["email"],
                 "Rekeningnummer": gegevens["rekeningnummer"], "DatumGemaakt": gegevens["datum"]},
                auto_regenerate=False,
            )

        # Onkosten invullen

        if onkosten is not None:
            if len(onkosten) > self.max_onkosten:
                raise Exception("Er zijn meer onkosten dan in de nota passen.")
            i = 1
            totaal = Decimal(0)
            for onkost in onkosten:
                # Field names
                boekhoudpost_field = "Boekhoudpost" + str(i)
                beschrijving_field = "Beschrijving" + str(i)
                prijs_field = "Prijs" + str(i)

                if onkost["boekhoudpost"] == self.boekhoudpost_vervoer:
                    if vervoersonkosten_vergoeding is None:
                        raise Exception("Vervoersonkosten vergoeding heeft geen waarde gekregen.")
                    eindprijs = onkost["prijs_of_km"] * vervoersonkosten_vergoeding
                else:
                    eindprijs = onkost["prijs_of_km"]
                writer.update_page_form_field_values(
                    writer.pages[0],
                    {boekhoudpost_field: onkost["boekhoudpost"], beschrijving_field: onkost["beschrijving"],
                     prijs_field: str(round_half_up(eindprijs, 2))},
                    auto_regenerate=False,
                )
                i += 1
                totaal += round_half_up(eindprijs, 2)

            writer.update_page_form_field_values(
                writer.pages[0],
                {"Totaal": str(totaal)},
                auto_regenerate=False,
            )

        if attachmentsdata is not None:
            for attachmentdata in attachmentsdata:
                if attachmentdata.read(len(self.pdf_signature)) == self.pdf_signature:
                    writer.append(fileobj=attachmentdata)
                else:
                    image = Image.open(attachmentdata)
                    pdf_buffer = io.BytesIO()
                    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
                    page_width, page_height = A4
                    image_width = image.width
                    image_height = image.height

                    if image_width > page_width or image_height > page_height:
                        if image_width > image_height:
                            ratio = page_width / image_width
                            image_height *= ratio
                            image_width = page_width
                        else:
                            ratio = page_height / image_height
                            image_width *= ratio
                            image_height = page_height

                    # (0,0) is lower left corner
                    x = 0
                    y = page_height - image_height

                    pdf.drawInlineImage(image=image, x=x, y=y, width=image_width, height=image_height)
                    pdf.save()
                    pdf_buffer.seek(0)
                    attachmentdata.write(pdf_buffer.read())
                    pdf_buffer.close()
                    writer.append(fileobj=attachmentdata)
                    attachmentdata.close()

        with open(savepath, "wb") as output_stream:
            writer.write(output_stream)
