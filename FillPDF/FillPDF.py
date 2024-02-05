import os
from decimal import Decimal
from typing import TypedDict

from pypdf import PdfReader, PdfWriter


class OnkostennotaOnkostenDictionary(TypedDict):
    """
    Dictionary die alle gegevens van de onkost opslaat, wordt ook gebruikt voor type hinting.

    :param boekhoudpost: De boekhoudpost waar de kost bij hoort.
    :param beschrijving: Beschrijving van de onkost.
    :param prijs_of_km: Aantal gereden kilometers in geval van transport, anders de prijs van de onkost.
    """
    boekhoudpost: str
    beschrijving: str
    prijs_of_km: Decimal


class OnkostennotaGegevensDictionary(TypedDict):
    """
    Dictionary die alle gegevens van de persoon die de onkosten gemaakt heeft opslaat, wordt ook gebruikt voor type hinting.

    :param voornaam: Voornaam van de persoon.
    :param naam: Achternaam van de persoon.
    :param email: Email van de persoon.
    :param rekeningnummer: Rekeningnummer van de persoon.
    :param datum: Datum dat de persoon de kosten heeft gemaakt.
    """
    voornaam: str
    naam: str
    email: str
    rekeningnummer: str
    datum: str


class FillPDF:
    def __init__(self) -> None:
        self.boekhoudpost_vervoer = "615000"
        self.max_onkosten = 16

    def fillOnkostennota(self, savepath: str, volgnummer: str = None, gegevens: OnkostennotaGegevensDictionary = None,
                         onkosten: list[OnkostennotaOnkostenDictionary] = None, betaaldatum: str = None,
                         vervoersonkosten_vergoeding: Decimal = None) -> None:
        """
        Functie die automatisch de onkostennota invult.

        :param savepath: Waar de onkostennota op te slaan.
        :param volgnummer: Volgnummer van de onkostennota.
        :param gegevens: Gegevens van de persoon die de onkosten gedaan heeft.
        :param onkosten: Lijst met de onkosten als dictionary. Maximaal 16.
        :param betaaldatum: Wanneer onkostennota effectief betaald wordt.
        :param vervoersonkosten_vergoeding: Hoeveel er per km vergoed wordt.
        """
        # Standaard variabelen, worden uit PDF gehaald
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        reader = PdfReader(os.path.join(template_dir, "Onkostennota.pdf"))
        writer = PdfWriter()
        writer.append(reader)

        # Vervoersvergoeding invullen
        writer.update_page_form_field_values(
            writer.pages[0],
            {"Vervoersonkosten": str(round(vervoersonkosten_vergoeding, 4))},
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
        i = 1
        totaal = Decimal(0)
        if onkosten is not None:
            if len(onkosten) > self.max_onkosten:
                raise Exception("Er zijn meer onkosten dan in de nota passen.")
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
                     prijs_field: str(round(eindprijs, 2))},
                    auto_regenerate=False,
                )
                i += 1
                totaal += round(eindprijs, 2)

            writer.update_page_form_field_values(
                writer.pages[0],
                {"Totaal": str(totaal)},
                auto_regenerate=False,
            )

        with open(savepath, "wb") as output_stream:
            writer.write(output_stream)
