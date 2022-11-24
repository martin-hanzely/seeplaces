import pytest

from seeplaces_service import SeePlacesService


class TestSeePlacesService:

    def test(self):
        with pytest.raises(NotImplementedError):
            _ = SeePlacesService()
