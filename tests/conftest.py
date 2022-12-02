import os
from typing import Any

import pytest

from seeplaces.service import SeePlacesOptions


class Cache:
    """
    Dummy class to mimic cache behavior.
    """
    _cache: dict[str, Any]

    def __init__(self):
        self._cache = dict()

    def get(self, key: str, *args, **kwargs) -> Any:
        return self._cache.get(key)

    def set(self, key: str, value: Any, *args, **kwargs) -> None:
        self._cache[key] = value


@pytest.fixture
def cache() -> Cache:
    """
    Dummy cache.
    """
    return Cache()


@pytest.fixture
def options() -> SeePlacesOptions:
    """
    Options fixture for testing. Takes agruments from environment.
    """
    try:
        return SeePlacesOptions(  # pylint:disable=E1123
            base_url=os.environ["BASE_URL"],
            api_version=os.environ["API_VERSION"],
            scope_id=os.environ["SCOPE_ID"],
        )
    except KeyError as exc:
        raise ValueError(f"Missing configuration key in environment: {exc}") from exc
