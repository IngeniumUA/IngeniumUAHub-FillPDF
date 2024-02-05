from decimal import Decimal
from typing import TypedDict

from pypdf import PdfReader, PdfWriter


class OnkostennotaOnkostenDictionary(TypedDict):
    boekhoudpost: str
    beschrijving: str
    prijs_of_km: Decimal


class OnkostennotaGegevensDictionary(TypedDict):
    voornaam: str
    naam: str
    email: str
    rekeningnummer: str
    datum: str


class FillPDF:
    def __init__(self) -> None:
        self.vervoersonkosten_vergoeding = 0.42
        self.boekhoudpost_vervoer = "615000"
        self.max_onkosten = 16

    def fillOnkostennota(self, savepath: str, volgnummer: str = None, gegevens: OnkostennotaGegevensDictionary = None,
                         onkosten: list[OnkostennotaOnkostenDictionary] = None, betaaldatum: str = None,) -> None:
        # Standaard variabelen, worden uit PDF gehaald


        reader = PdfReader("Templates/Onkostennota.pdf")
        writer = PdfWriter()
        writer.append(reader)

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
        i = 1
        totaal = 0
        if onkosten is not None:
            if len(onkosten) > self.max_onkosten:
                raise Exception("Er zijn meer onkosten dan in de nota passen.")
            for onkost in onkosten:
                # Field names
                boekhoudpost_field = "Boekhoudpost" + str(i)
                beschrijving_field = "Beschrijving" + str(i)
                prijs_field = "Prijs" + str(i)

                if onkost["boekhoudpost"] == self.boekhoudpost_vervoer:
                    eindprijs = onkost["prijs_of_km"] * self.vervoersonkosten_vergoeding
                else:
                    eindprijs = onkost["prijs_of_km"]
                totaal += eindprijs

                writer.update_page_form_field_values(
                    writer.pages[0],
                    {boekhoudpost_field: onkost["boekhoudpost"], beschrijving_field: onkost["beschrijving"],
                     prijs_field: str(round(eindprijs, 2))},
                    auto_regenerate=False,
                )
                i += 1

            writer.update_page_form_field_values(
                writer.pages[0],
                {"Totaal": totaal},
                auto_regenerate=False,
            )

        with open(savepath, "wb") as output_stream:
            writer.write(output_stream)
