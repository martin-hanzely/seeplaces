import os
from collections.abc import Iterator
from unittest import mock

import pytest
import requests

from seeplaces_service import (
    ConfigurationError,
    SeePlacesOptions,
    _SpokenLanguage,
    SeePlacesService,
)


_test_base_url = "https://www.example.com/"


@pytest.fixture(autouse=True)
def setup_env() -> Iterator[None]:
    """
    Dummy testing environment.
    """
    required_env = {
        "BASE_URL": _test_base_url,  # Must end with trailing slash.
        "API_VERSION": "1.0",
    }
    with mock.patch.dict(os.environ, required_env):
        yield


class TestSeePlacesOptions:

    def test_init(self):
        options = SeePlacesOptions()        
        assert options.base_url == _test_base_url

    def test_init_fails(self):
        missing_env = "BASE_URL"
        _env = {k: v for k, v in os.environ.items()}
        _ = dict.pop(_env, missing_env)
        with mock.patch.dict(os.environ, _env, clear=True):
            with pytest.raises(ConfigurationError) as exc:
                _ = SeePlacesOptions()
                assert missing_env in str(exc)


class TestSeePlacesService:

    @pytest.fixture
    def service(self, setup_env) -> SeePlacesService:
        options = SeePlacesOptions()
        return SeePlacesService(options=options)

    def test__get_language_ids(self, monkeypatch, service):
        test_id = "test_id"
        languages = [
            _SpokenLanguage(test_id, "Slovak", "slovak"),
            _SpokenLanguage("test_id1", "Czech", "czech")
        ]
        monkeypatch.setattr(service, "_call_excursion_spoken_languages", lambda: None)
        monkeypatch.setattr(service, "_parse_languages_from_response", lambda _: languages)
        language_ids = service._get_language_ids({"Slovak"})
        assert len(language_ids) == 1
        assert language_ids.pop() == test_id

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
                [_SpokenLanguage("test_id", "Slovak", "slovak")],
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
