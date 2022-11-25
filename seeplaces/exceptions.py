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
