import datetime
import os
from collections.abc import Iterator
from unittest import mock

import pytest
import requests

from seeplaces.service import _SpokenLanguage, SeePlacesService


@pytest.fixture()
def setup_env() -> Iterator[None]:
    """
    Dummy testing environment.
    """
    # Only use in unit tests. Integration needs real values.
    required_env = {
        "BASE_URL": "https://www.example.com/",  # Must end with trailing slash.
        "API_VERSION": "1.0",
        "SCOPE_ID": "123456",
    }
    with mock.patch.dict(os.environ, required_env):
        yield


class TestSeePlacesService:

    @pytest.fixture
    def service(self, cache, setup_env, options) -> SeePlacesService:
        """
        Dummy service with test values.
        """
        return SeePlacesService(options=options, cache=cache)

    def test__get_language_ids(self, monkeypatch, service):
        # Disable cache.
        service._cache = None

        test_id = "test_id"
        languages = [
            _SpokenLanguage(Id=test_id, Name="Slovak"),
            _SpokenLanguage(Id="test_id1", Name="Czech")
        ]
        monkeypatch.setattr(service, "_call_excursion_spoken_languages", lambda: None)
        monkeypatch.setattr(service, "_parse_languages_from_response", lambda _: languages)
        language_ids = service._get_language_ids(["Slovak"])
        assert len(language_ids) == 1
        assert language_ids.pop() == test_id

    def test__get_language_ids__from_cache(self, monkeypatch, cache, service):
        cached_value = "cached_value"
        cache.set(service._languages_cache_key(["Slovak"]), cached_value)
        assert cached_value == service._get_language_ids(["Slovak"])

    def test__excursions_cache_key(self, service):
        key = service._excursions_cache_key("BTS", datetime.date(2023, 1, 1), ["Slovak", "Czech"])
        assert key == "seeplaces_exc_BTS_1_SloCze"

    @pytest.mark.parametrize(
        "languages, expected_output",
        [
            ([], "seeplaces_lang_"),
            (["Slovak"], "seeplaces_lang_Slo"),
            (["Slovak", "Czech"], "seeplaces_lang_SloCze"),
        ]
    )
    def test__languages_cache_key(self, service, languages, expected_output):
        assert service._languages_cache_key(languages) == expected_output

    @pytest.mark.parametrize(
        "json_data, expected_output",
        [
            pytest.param(
                {},
                [],
                id="empty_response",
            ),
            pytest.param(
                {"SpokenLanguages": [{"Id": "test_id", "Name": "Slovak", "UrlName": "slovak"}]},
                [_SpokenLanguage(Id="test_id", Name="Slovak")],
                id="response_from_api_docs",
            ),
        ]
    )
    def test__parse_languages_from_response(self, service, json_data, expected_output):

        class _MockResponse:

            def json(self):
                return json_data

        languages = service._parse_languages_from_response(response=_MockResponse())
        assert len(languages) == len(expected_output)
        if len(languages) > 0:
            assert languages[0].id == expected_output[0].id

    @pytest.mark.parametrize(
        "status_code",
        [
            pytest.param(200, id="status_ok"),
            pytest.param(404, marks=pytest.mark.xfail, id="status_not_found"),
        ]
    )
    def test__call_api(self, monkeypatch, service, status_code):
        response = requests.Response()
        response.status_code = status_code
        monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)
        _ = service._call_api(endpoint="", query={}, headers={})
