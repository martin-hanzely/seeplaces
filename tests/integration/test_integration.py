import datetime

import pytest

from seeplaces.excursion import SeePlacesExcursion
from seeplaces.service import SeePlacesService


class TestIntegration:

    @pytest.fixture
    def service(self, options) -> SeePlacesService:
        """
        Service with real values for integration tests.
        """
        return SeePlacesService(options=options)    

    def test_get_excursions(self, service):
        """
        Check if ExcursionForIataCode response is parsed into SeePlacesExcursion objects.
        """
        _today = datetime.date.today()
        excursions = service.get_excursions(
            iata_code="AYT",
            date_from=_today,
            date_to=_today + datetime.timedelta(days=7),
            spoken_languages=["Slovak"],
        )

        # Assume some excursions are always returned.
        assert len(excursions) > 0, "No excursions found"
        for excursion in excursions:
            assert isinstance(excursion, SeePlacesExcursion), "Wrong return type."

    def test__excursion_spoken_languages(self, service):
        """
        Check if ExcursionSpokenLanguages api response has expected format.
        """
        api_response = service._call_excursion_spoken_languages()
        all_languages = service._parse_languages_from_response(api_response)
        assert len(all_languages) > 0, "No languages found."

        found_slovak = False
        for _l in all_languages:
            assert isinstance(_l.id, str)
            assert isinstance(_l.name, str)
            if _l.name == "Slovak":
                found_slovak = True
        assert found_slovak, "Slovak language not found."

    def test__call_excursion_for_iata_code(self, service):
        """
        Check if ExcursionForIataCode api response has expected format.
        """
        language_ids = service._get_language_ids(["Slovak"])
        assert len(language_ids) > 0, "No languages found."

        _today = datetime.date.today()
        api_response = service._call_excursion_for_iata_code(
            iata_code="AYT",
            date_from=_today,
            date_to=_today + datetime.timedelta(days=7),
            language_ids=language_ids,
        )
        json_data = api_response.json()

        items = json_data.get("Items")
        assert items is not None, "Items key not found."
        assert isinstance(items, list), "Items is not a list."

        total = json_data.get("Total")
        assert total is not None, "Total key not found."
        if total > 0:
            assert isinstance(total, int), "Total is not an integer."
            assert len(items) == total, "Total does not match number of items."
