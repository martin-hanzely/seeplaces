import datetime
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urljoin

import requests

from seeplaces.exceptions import ApiConnectionError
from seeplaces.excursion import SeePlacesExcursion


LANGUAGES_CACHE_TTL = 60 * 60 * 24  # 24 hours.
EXCURSIONS_CACHE_TTL = 60 * 60  # 1 hour.


_mapping = dict[str, Any]
"""Type alias for mappings, eg. query and headers."""


class CacheProtocol(Protocol):
    """
    Generic cache protocol designed to be used with Django cache API.
    See: https://docs.djangoproject.com/en/3.2/topics/cache/#the-low-level-cache-api.
    """
    def get(self, key: str, default: Any | None = None, version: Any = None) -> Any: ...
    def set(self, key: str, value: Any, timeout: int = 0, version: Any = None) -> None: ...
    """Generic integer placeholder used as DEFAULT_TIMEOUT."""


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

    # Require keyword arguments. Discard unused input.
    def __init__(self, *, Id: str, Name: str, **_) -> None:  # pylint: disable=C0103
        self.id = Id
        self.name = Name


class SeePlacesService:
    """
    Connection service for SeePlaces API.
    """
    _options: SeePlacesOptions
    _cache: CacheProtocol | None
    _cache_prefix: str

    def __init__(
            self,
            options: SeePlacesOptions,
            cache: CacheProtocol | None = None,
            cache_prefix: str | None = None,
    ) -> None:
        self._options = options
        self._cache = cache

        # Do not use "argument or default" as empty prefix should be allowed.
        if cache_prefix is None:
            cache_prefix = "seeplaces"  # Default cache prefix.
        self._cache_prefix = cache_prefix

    def get_excursions(
        self,
        iata_code: str,
        date_from: datetime.date,
        date_to: datetime.date,
        spoken_languages: list[str],
    ) -> list[SeePlacesExcursion]:
        """
        Returns list of SeePlacesExcursion objects from api.
        """
        # Search for result in cache.
        cache_key = self._excursions_cache_key(iata_code, date_from, spoken_languages)
        if (cache := self._cache) and (cached_result := cache.get(cache_key)):
            return cached_result

        # Get result from API.
        language_ids = self._get_language_ids(spoken_languages=spoken_languages)
        api_response = self._call_excursion_for_iata_code(
            iata_code=iata_code,
            date_from=date_from,
            date_to=date_to,
            language_ids=language_ids,
        )
        json_data: dict[str, Any] = api_response.json()

        excursions = []
        # Assuming Items is iterable.
        if excursions_from_response := json_data.get("Items"):
            for _e in excursions_from_response:
                excursions.append(SeePlacesExcursion(**_e))

        # Save result to cache.
        if cache is not None:
            cache.set(cache_key, excursions, timeout=EXCURSIONS_CACHE_TTL)

        return excursions

    def _get_language_ids(self, spoken_languages: list[str]) -> set[str]:
        """
        Returns IDs of given languages. Tries to hit cache first. Saves result to cache.
        """
        # Search for result in cache.
        cache_key = self._languages_cache_key(spoken_languages)
        if (cache := self._cache) and (cached_result := cache.get(cache_key)):
            return cached_result

        # Get result from API.
        api_response = self._call_excursion_spoken_languages()
        all_languages = self._parse_languages_from_response(api_response)
        language_ids = {_l.id for _l in all_languages if _l.name in spoken_languages}

        # Save result to cache.
        if cache is not None:
            cache.set(cache_key, language_ids, timeout=LANGUAGES_CACHE_TTL)

        return language_ids

    def _excursions_cache_key(
        self,
        iata_code: str,
        date_from: datetime.date,
        spoken_languages: list[str],
    ) -> str:
        """
        Returns cache key for excursions.
        """
        lang_code = "".join(_l[:3] for _l in spoken_languages)
        return f"{self._cache_prefix}_exc_{iata_code}_{date_from.month}_{lang_code}"

    def _languages_cache_key(self, spoken_languages: list[str]) -> str:
        """
        Returns cache key for languages.
        """
        code = "".join(_l[:3] for _l in spoken_languages)
        return f"{self._cache_prefix}_lang_{code}"

    def _parse_languages_from_response(self, response: requests.Response) -> list[_SpokenLanguage]:
        """
        Returns api call response parsed into list of _SpokenLanguage objects.
        """
        json_data: dict[str, Any] = response.json()

        languages = []
        # Assuming SpokenLanguages is iterable.
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
