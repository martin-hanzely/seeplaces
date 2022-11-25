import os
from typing import Any
from urllib.parse import urljoin

import requests


_mapping = dict[str, Any]
"""Type alias for mappings, eg. query and headers."""


class SeePlacesError(Exception):
    """
    Generic SeePlaces service exception.
    """


class ConfigurationError(SeePlacesError):
    """
    Service configuration error.
    """


class ApiConnectionError(SeePlacesError):
    """
    Service connection error.
    """


class SeePlacesOptions:
    """
    Internal options class for SeePlaces service.
    """
    base_url: str
    api_version: str

    def __init__(self) -> None:
        try:
            self.base_url = os.environ["BASE_URL"]
            self.api_version = os.environ["API_VERSION"]
        except KeyError as exc:
            raise ConfigurationError(f"Missing configuration key: {exc}") from exc


class _SpokenLanguage:
    """
    Internal class for handling spoken languages.
    """
    id: str
    name: str
    url_name: str

    def __init__(self, Id: str, Name: str, UrlName: str) -> None:  # pylint: disable=C0103
        self.id = Id
        self.name = Name
        self.url_name = UrlName


class SeePlacesService:
    """
    Connection service for SeePlaces API.
    """
    _options: SeePlacesOptions

    def __init__(self, options: SeePlacesOptions) -> None:
        self._options = options

    def _get_language_ids(self, languages: set[str]) -> set[str]:
        """
        Returns IDs of given languages.
        """
        api_response = self._call_excursion_spoken_languages()
        all_languages = self._parse_languages_from_response(api_response)
        return {_l.id for _l in all_languages if _l.name in languages}

    def _parse_languages_from_response(self, response: requests.Response) -> list[_SpokenLanguage]:
        """
        Returns api call response parsed into list of _SpokenLanguage objects.
        """
        json_data: dict[str, Any] = response.json()

        languages = []
        if languages_from_response := json_data.get("SpokenLanguages"):
            for _l in languages_from_response:
                languages.append(_SpokenLanguage(**_l))
        return languages

    def _call_api(self, endpoint: str, query: _mapping, headers: _mapping) -> requests.Response:
        """
        Generic api call with provided parameters.
        """
        base_url = self._options.base_url
        response = requests.get(
            urljoin(base_url, endpoint),
            params=query,
            headers={"accept": "application/json"} | headers,  # Override defaults with parameter.
            timeout=60,
        )
        try:
            response.raise_for_status()  # Raise exception if response status is not OK.
        except requests.HTTPError as exc:
            raise ApiConnectionError(f"Cannot connect to endpoint: {endpoint}") from exc
        return response

    def _call_excursion_spoken_languages(self) -> requests.Response:
        """
        Returns response of ExcursionSpokenLanguages api call.
        """
        endpoint_path = "api/Excursion/ExcursionSpokenLanguages"
        query = {"api-version": self._options.api_version}
        return self._call_api(endpoint=endpoint_path, query=query, headers={})

    def _call_excursion_for_iata_code(self) -> requests.Response:
        """
        Returns response of ExcursionForIataCode api call.
        """
        raise NotImplementedError
