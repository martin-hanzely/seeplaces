import os

import pytest

from seeplaces.service import SeePlacesOptions


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
