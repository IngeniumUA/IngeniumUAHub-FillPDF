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
