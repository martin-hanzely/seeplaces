from dataclasses import dataclass


@dataclass
class _ExcursionDuration:
    """
    Excursion duration settings.
    """
    is_all_day: bool
    is_many_days: bool
    duration_hours: float
    duration_days: float
    hide_duration: bool

    def readable(self) -> str:
        """
        Returns duration in readable format.
        """
        # Duration should be hidden.
        if self.hide_duration:
            return "Nie je k dispozícii"

        # Multiple days. Should include days count.
        if self.is_many_days:
            return f"Počet dní: {self.duration_days:.2f}"

        # All day. No need to cound hours or days.
        if self.is_all_day:
            return "Celý deň"

        # Multiple hours. SHould include hours count.
        return f"Počet hodín: {self.duration_hours:.2f}"


class SeePlacesExcursion:
    """
    Excursion class returned from SeePlaces Excursion api call.
    """
    # Do not use defaults. All parameters should be present in response.
    name: str
    final_price: float
    photo_path: str
    description: str
    currency: str
    included_in_price: list[str]

    _duration: _ExcursionDuration

    def __init__(
        self,
        *,  # Require keyword arguments.
        Name,
        FinalPrice,
        PhotoPath,
        Description,
        Currency,
        IncludedInPrice,
        IsAllDay,
        IsManyDays,
        DurationHours,
        DurationDays,
        HideDuration,
        **_,  # Discard unused input.
    ) -> None:
        """
        Maps api call response to class properties. Discards unused response properties.
        """
        self.name = Name
        self.final_price = FinalPrice
        self.photo_path = PhotoPath
        self.description = Description
        self.currency = Currency
        self.included_in_price = IncludedInPrice
        self._duration = _ExcursionDuration(
            is_all_day=IsAllDay,
            is_many_days=IsManyDays,
            duration_hours=DurationHours,
            duration_days=DurationDays,
            hide_duration=HideDuration,
        )

    def get_duration_display(self) -> str:
        """
        Returns duration in readable format.
        """
        return self._duration.readable()
