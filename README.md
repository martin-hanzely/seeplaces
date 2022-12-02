# seeplaces

Python wrapper for [seeplaces.com](https://seeplaces.com/) excursion api.

## Quick start

1. Create `SeePlacesOptions` instance:
    ```python
    from seeplaces.service import SeePlacesOptions

    options = SeePlacesOptions(
        base_url="https://www.example.com/",  # Must end with trailing slash.
        api_version="1.0",
        scope_id="123456",
    )
    ```
1. Create `SeePlacesService` instance (optionally with cache framework):
    ```python
   from django.core.cache import cache
   from seeplaces.service import SeePlacesService

    service = SeePlacesService(options=options, cache=cache)
    ```
1. Get `list` of `SeePlacesExcursion` instances:
    ```python
    import datetime
    from seeplaces.excursion import SeePlacesExcursion

    excursions: list[SeePlacesExcursion] = service.get_excursions(
        iata_code="BTS",
        date_from=datetime.date(2023, 1, 1),
        date_to=datetime.date(2023, 12, 31),
        languages=["Slovak"],
    )
    ```
