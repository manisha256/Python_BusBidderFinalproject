class BusBidderError(Exception):
    """Base exception for BusBidder application."""
    pass

class InvalidDestinationError(BusBidderError):
    """Raised when an offer references an unknown destination."""
    pass

class InvalidOfferDataError(BusBidderError):
    """Raised when offer data contains impossible values (e.g., negative price, invalid dates)."""
    pass

class TimeConsistencyError(BusBidderError):
    """Raised when arrival time is earlier than or equal to departure time."""
    pass

class SeatAvailabilityError(BusBidderError):
    """Raised when an offer has zero or negative available seats."""
    pass