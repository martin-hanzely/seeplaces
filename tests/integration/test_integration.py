from seeplaces.service import SeePlacesOptions, SeePlacesService


class TestIntegration:

    def test_excursion_spoken_languages(self):
        """
        Check if ExcursionSpokenLanguages api response has expected format.
        """
        options = SeePlacesOptions()
        service = SeePlacesService(options=options)
        api_response = service._call_excursion_spoken_languages()
        all_languages = service._parse_languages_from_response(api_response)
        assert len(all_languages) > 0
        for _l in all_languages:
            assert isinstance(_l.id, str)
            assert isinstance(_l.name, str)
            assert isinstance(_l.url_name, str)
