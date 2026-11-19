from custom_logger import log_event

def filter_offers(offers: list, profile) -> list:
    """
    Applies MANDATORY HARD CONSTRAINTS to eliminate invalid offers prior to MCDM ranking.
    
    Design Responsibility & Justification:
      - Hard constraints represent physical limits, legal/logistical requirements, or 
        strict user non-negotiables (destination, travel window, seat availability, budget ceiling, 
        max transfers, max duration, mandatory luggage, and mandatory ticket changeability). 
      - Offers violating any of these are fundamentally unusable and are filtered out completely 
        before multi-criteria scoring.
    """
    filtered = []
    start_date, end_date = profile.travel_window
    rejected_counts = {
        "destination": 0, "date_window": 0, "seats": 0, 
        "budget": 0, "transfers": 0, "duration": 0, 
        "luggage": 0, "changeable": 0
    }

    for offer in offers:
        # 1. Destination Match
        if offer.destination.strip().lower() != profile.destination.strip().lower():
            rejected_counts["destination"] += 1
            continue

        # 2. Travel Date Window
        if not (start_date <= offer.date <= end_date):
            rejected_counts["date_window"] += 1
            continue

        # 3. Seat Availability
        if offer.seats < profile.min_seats:
            rejected_counts["seats"] += 1
            continue

        # 4. Maximum Budget Ceiling
        if offer.price > profile.max_budget:
            rejected_counts["budget"] += 1
            continue

        # 5. Maximum Transfers Allowed
        if offer.transfers > profile.max_transfers:
            rejected_counts["transfers"] += 1
            continue

        # 6. Maximum Trip Duration (in minutes)
        if offer.duration > profile.max_duration:
            rejected_counts["duration"] += 1
            continue

        # 7. Mandatory Luggage Allowance
        if profile.require_luggage and not offer.luggage:
            rejected_counts["luggage"] += 1
            continue

        # 8. Mandatory Ticket Flexibility (Changeable)
        if profile.require_changeable and not offer.changeable:
            rejected_counts["changeable"] += 1
            continue

        filtered.append(offer)

    log_event(f"Hard constraints filtering completed. {len(filtered)} offers passed. Rejections summary: {rejected_counts}")
    return filtered