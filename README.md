# seeplaces

## Quick start

1. Create `SeePlacesOptions` instance:
    ```python
    from seeplaces import SeePlacesOptions

    options = SeePlacesOptions(
        base_url="https://www.example.com/",  # Must end with trailing slash.
        api_version="1.0",
        scope_id="123456",
    )
    ```
1. Create `SeePlacesService` instance:
    ```python
    from seeplaces import SeePlacesService

    service = SeePlacesService(options=options)
    ```
