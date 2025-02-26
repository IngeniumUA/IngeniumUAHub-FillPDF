import io
import math
from decimal import Decimal
from typing import TypedDict
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


class AttachmentData(TypedDict):
    naam: str
    data: bytes


def round_half_up(number, decimals=2):
    multiplier = Decimal(10 ** decimals)
    return math.floor(number * multiplier + Decimal(0.5)) / multiplier


class FillOnkostennota:
    def __init__(self) -> None:
        self.boekhoudpost_vervoer = "615000"
        self.max_onkosten = 16
        self.pdf_signature = b"%PDF-"

    def fill(self, filedata: io.BytesIO, savepath: str, volgnummer: str = None,
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


class Factuur:
    def __init__(self) -> None:
        self.max_producten = 10

    def fill(self, filedata: str, savepath: str, volgnummer: str = None, factuurdatum: str = None,
             naar: FactuurNaar = None,
             producten: list[
                 FactuurGegevens] = None, dagen: str = None) -> None:
        """
        Functie die automatisch de factuur template invult.

        :param filedata: Data van het te bewerken bestand.
        :param savepath: Waar de factuur op te slaan.
        :param volgnummer: Volgnummer van de factuur.
        :param factuurdatum: Datum dat de factuur is opgesteld.
        :param naar: Gegevens van de factuurontvanger.
        :param producten: Lijst van verkochte producten.
        :param dagen: Aantal dagen dat de factuur binnen betaald moet worden.
        """
        # Standaard variabelen, worden uit PDF gehaald
        reader = PdfReader(filedata)
        writer = PdfWriter()
        writer.append(reader)

        # Volgnummer invullen
        if volgnummer is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Volgnummer": volgnummer},
                auto_regenerate=False,
            )

        # Factuurdatum invullen
        if factuurdatum is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Factuurdatum": volgnummer},
                auto_regenerate=False,
            )

        # Dagen invullen
        if dagen is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Betaaldagen": dagen},
                auto_regenerate=False,
            )

        # Naar invullen
        if naar is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Begunstigde": naar["begunstigde"], "Adres1": naar["adres1"],
                 "Adres2": naar["adres2"]},
                auto_regenerate=False,
            )
            if naar["btw"] is not None:
                writer.update_page_form_field_values(
                    writer.pages[0],
                    {"BTW": naar["btw"]},
                    auto_regenerate=False,
                )
            if naar["ordernummer"] is not None:
                writer.update_page_form_field_values(
                    writer.pages[0],
                    {"OrderNummer": naar["ordernummer"]},
                    auto_regenerate=False,
                )
            if naar["begunstigde"] is not None:
                writer.update_page_form_field_values(
                    writer.pages[0],
                    {"Departement": naar["departement"]},
                    auto_regenerate=False,
                )

        if producten is not None:
            if len(producten) > self.max_producten:
                raise Exception("Er zijn meer producten dan in de factuur passen.")
            i = 1
            totaal_inclusief = Decimal(0)
            totaal_exclusief = Decimal(0)

            for product in producten:
                # Field names
                boekhoudpost_field = "Boekhoudpost" + str(i)
                beschrijving_field = "Beschrijving" + str(i)
                prijs_field = "Prijs" + str(i)
                aantal_field = "Aantal" + str(i)
                btw_field = "BTW" + str(i)
                totaal_field = "Totaal" + str(i)

                # Prijs berekening
                totaal_product = product["prijs"] * product["aantal"]
                totaal_exclusief += totaal_product
                totaal_product = totaal_product * (1 + product["btw"] / 100)
                totaal_inclusief += totaal_product

                writer.update_page_form_field_values(
                    writer.pages[0],
                    {boekhoudpost_field: product["boekhoudpost"], beschrijving_field: product["beschrijving"],
                     prijs_field: product["prijs"], aantal_field: product["aantal"], btw_field: product["btw"],
                     totaal_field: str(round_half_up(totaal_product, 2))},
                    auto_regenerate=False,
                )
                i += 1

            writer.update_page_form_field_values(
                writer.pages[0],
                {"TotaalExclusief": str(round_half_up(totaal_exclusief, 2)),
                 "TotaalInclusief": str(round_half_up(totaal_inclusief, 2))},
                auto_regenerate=False,
            )

        with open(savepath, "wb") as output_stream:
            writer.write(output_stream)


class Huurcontract:
    def __init__(self) -> None:
        self.max_verhuur = 10

    def fill(self, filedata: str, savepath: str, volgnummer: str = None, huurder_gegevens: HuurderGegevens = None,
             verhuurde_producten: list[HuurcontractGegevens] = None, startdatum: str = None, einddatum: str = None,
             huurprijs: Decimal = None, waarborg: Decimal = None, verhuurder: str = None, huurder: str = None) -> None:
        # Standaard variabelen, worden uit PDF gehaald
        reader = PdfReader(filedata)
        writer = PdfWriter()
        writer.append(reader)
        writer.set_need_appearances_writer(True)

        # Volgnummer invullen
        if volgnummer is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Volgnummer1": volgnummer},
                auto_regenerate=False,
            )
            writer.update_page_form_field_values(
                writer.pages[1],
                {"Volgnummer2": volgnummer, "Volgnummer3": volgnummer},
                auto_regenerate=False,
            )

        # Huurder gegevens invullen
        if huurder_gegevens is not None:
            if huurder_gegevens["btw"] is not None:
                writer.update_page_form_field_values(
                    writer.pages[0],
                    {"BTWHuurder": huurder_gegevens["btw"]},
                    auto_regenerate=False,
                )
            writer.update_page_form_field_values(
                writer.pages[0],
                {"AdresHuurder": huurder_gegevens["adres"], "NaamHuurder1": huurder_gegevens["naam"]},
                auto_regenerate=False,
            )

        # Verhuurde producten invullen
        if verhuurde_producten is not None:
            if len(verhuurde_producten) > self.max_verhuur:
                raise Exception("Er zijn meer producten dan in het contract passen.")
            i = 1
            for verhuurd_product in verhuurde_producten:
                # Field names
                materiaal_field = "Materiaal" + str(i)
                opmerkingen_field = "Opmerkingen" + str(i)
                schade_field = "Schade" + str(i)
                schadeprijs = str(round_half_up(verhuurd_product["schadeprijs"])) + " €/stuk"

                writer.update_page_form_field_values(
                    writer.pages[0],
                    {materiaal_field: verhuurd_product["materiaal"], opmerkingen_field: verhuurd_product["opmerkingen"],
                     schade_field: schadeprijs},
                    auto_regenerate=False,
                )
                i += 1

        # Datum invullen
        if startdatum is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Startdatum": startdatum},
                auto_regenerate=False,
            )

        if einddatum is not None:
            writer.update_page_form_field_values(
                writer.pages[0],
                {"Einddatum": einddatum},
                auto_regenerate=False,
            )

        # Prijzen invullen
        if huurprijs is not None:
            if startdatum is not None:
                writer.update_page_form_field_values(
                    writer.pages[1],
                    {"Huurprijs": str(round_half_up(huurprijs))},
                    auto_regenerate=False,
                )

        if waarborg is not None:
            if startdatum is not None:
                writer.update_page_form_field_values(
                    writer.pages[1],
                    {"Waarborg": str(round_half_up(waarborg))},
                    auto_regenerate=False,
                )

        # Handtekening gegevens invullen
        if verhuurder is not None:
            writer.update_page_form_field_values(
                writer.pages[1],
                {"NaamIngenium1": verhuurder, "NaamIngenium2": verhuurder},
                auto_regenerate=False,
            )

        if huurder is not None:
            writer.update_page_form_field_values(
                writer.pages[1],
                {"NaamHuurder2": huurder, "NaamHuurder3": huurder},
                auto_regenerate=False,
            )

        with open(savepath, "wb") as output_stream:
            writer.write(output_stream)
