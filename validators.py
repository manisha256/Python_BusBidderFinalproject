class BusBidderError(Exception):
    """Base exception for BusBidder application."""
    pass

class InvalidPriceError(BusBidderError):
    pass

class InvalidOfferError(BusBidderError):
    pass

class WeightValidationError(BusBidderError):
    pass

def validate_weights(weights: dict):
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-5:
        raise WeightValidationError(f"Weights must sum to 1.0 (currently {total})")
    return True