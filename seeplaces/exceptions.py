class SeePlacesError(Exception):
    """
    Generic SeePlaces service exception.
    """


class ApiConnectionError(SeePlacesError):
    """
    Service connection error.
    """
