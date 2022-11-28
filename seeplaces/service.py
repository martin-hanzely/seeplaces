import datetime
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests

from seeplaces.exceptions import ApiConnectionError


_mapping = dict[str, Any]
"""Type alias for mappings, eg. query and headers."""


@dataclass
class SeePlacesOptions:
    """
    Internal options class for SeePlaces service.
    """
    base_url: str
    api_version: str
    scope_id: str


class _SpokenLanguage:
    """
    Internal class for handling spoken languages.
    """
    id: str
    name: str

    # Require positional arguments. Discard unused input.
    def __init__(self, *, Id: str, Name: str, **_) -> None:  # pylint: disable=C0103
        self.id = Id
        self.name = Name


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
        Generic api call with provided parameters. Parameters override query and header defaults.
        """
        base_url = self._options.base_url
        response = requests.get(
            urljoin(base_url, endpoint),
            params={"api-version": self._options.api_version} | query,
            headers={"accept": "application/json"} | headers,
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
        # English is accepted here. Customers do not see the response.
        headers = {"accept-language": "en-US"}
        return self._call_api(endpoint=endpoint_path, query={}, headers=headers)

    def _call_excursion_for_iata_code(
            self,
            iata_code: str,
            date_from: datetime.date,
            date_to: datetime.date,
            language_ids: set[str],
    ) -> requests.Response:
        """
        Returns response of ExcursionForIataCode api call.
        """
        endpoint_path = "api/Excursion/ExcursionForIataCode"
        query = {
            "input.iataCodes": iata_code,
            "input.dateFrom": date_from.isoformat(),
            "input.dateTo": date_to.isoformat(),
            "input.spokenLanguages": language_ids,
        }
        headers = {
            "x-scope-id": self._options.scope_id,
            "currency": "EUR",
            "accept-language": "sk-SK",  # Slovak is needed for customers.
        }
        return self._call_api(endpoint=endpoint_path, query=query, headers=headers)
