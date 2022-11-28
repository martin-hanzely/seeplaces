import pytest

from seeplaces.excursion import SeePlacesExcursion


class TestSeePlacesExcursion:

    @pytest.fixture
    def excursion(self) -> SeePlacesExcursion:
        return SeePlacesExcursion(
            Name="Test Excursion",
            FinalPrice=100.0,
            PhotoPath="https://example.com/img.jpg",
            Description="Test description.",
            Currency="EUR",
            IncludedInPrice=["Guide"],
            IsAllDay=False,
            IsManyDays=False,
            DurationHours=0.0,
            DurationDays=0.0,
            HideDuration=False,
        )

    @pytest.mark.parametrize(
        "duration_settings, expected_output",
        [
            pytest.param(
                {"hide_duration": True}, "Nie je k dispozícii", id="unavailable"
            ),
            pytest.param(
                {"is_many_days": True, "duration_days": 5.5}, "Počet dní: 5.50", id="multiple_days"
            ),
            pytest.param(
                {"is_all_day": True}, "Celý deň", id="all_day"
            ),
            pytest.param(
                {"duration_hours": 5.5}, "Počet hodín: 5.50", id="multiple_hours"
            ),
        ]
    )
    def test_get_duration_display(self, excursion, duration_settings, expected_output):
        for k, v in duration_settings.items():
            setattr(excursion._duration, k, v)  # Update duration with given settings.
            
        assert excursion.get_duration_display() == expected_output
