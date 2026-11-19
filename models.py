class Company:
    def __init__(self, name: str, profile: str):
        self.name = name
        self.profile = profile

class Destination:
    def __init__(self, name: str, region: int):
        self.name = name
        self.region = region

class Offer:
    def __init__(self, company: str, destination: str, date: str,
                 departure_time: str, arrival_time: str, duration: int,
                 price: float, transfers: int, luggage: bool,
                 changeable: bool, refundable: bool, seats: int, rating: float):
        self.company = company
        self.destination = destination
        self.date = date
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.duration = duration      # in minutes
        self.price = price            # in EUR
        self.transfers = transfers
        self.luggage = luggage
        self.changeable = changeable
        self.refundable = refundable
        self.seats = seats            # Available seats per offer
        self.rating = rating

class TravellerProfile:
    def __init__(self, origin: str, destination: str, travel_window: tuple,
                 max_budget: float, min_seats: int, max_transfers: int,
                 require_luggage: bool, max_duration: int, require_changeable: bool,
                 preferred_time: str, weights: dict):
        # --- HARD CONSTRAINTS (Mandatory Eliminatory Filters) ---
        self.origin = origin
        self.destination = destination
        self.travel_window = travel_window          # Start and End date bounds
        self.max_budget = max_budget                # Price ceiling per ticket
        self.min_seats = min_seats                  # Minimum seat availability required
        self.max_transfers = max_transfers          # Maximum transfers allowed
        self.require_luggage = require_luggage      # Mandatory luggage inclusion
        self.max_duration = max_duration            # Maximum trip duration in minutes
        self.require_changeable = require_changeable # Mandatory ticket flexibility

        # --- SOFT PREFERENCES (MCDM Weighted Scoring Criteria) ---
        self.preferred_time = preferred_time
        self.weights = weights  # Summing to 1.0 (price, duration, time, flexibility)