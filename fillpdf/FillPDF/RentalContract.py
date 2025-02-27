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