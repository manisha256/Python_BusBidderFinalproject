# import csv
# import os
# import random
# import re
# from datetime import datetime, timedelta
# from models import Destination, Offer, Company
# from custom_logger import log_event, log_rejection

# DATA_DIR = os.path.join(os.getcwd(), "data")

# MADRID_DISTANCES = {
#     "barcelona": 620,
#     "valencia": 355,
#     "seville": 530,
#     "malaga": 530,
#     "granada": 420,
#     "cordoba": 400,
#     "bilbao": 400,
#     "san sebastian": 460,
#     "zaragoza": 320,
#     "alicante": 420,
#     "murcia": 400,
#     "salamanca": 215,
#     "toledo": 75,
#     "santiago de compostela": 600,
#     "cadiz": 650,
# }

# # Carrier profiles matching the BusBidder Spain specification
# COMPANY_PROFILES = {
#     "SolRuta": {
#         "description": "Low-cost daytime services",
#         "speed_kmh": 75.0,
#         "price_per_km": 0.09,
#         "dep_hours": list(range(7, 18)),   # Daytime departures
#         "transfers_pool": [0, 1, 2],
#     },
#     "Camino Express": {
#         "description": "Fast direct connections between major cities",
#         "speed_kmh": 85.0,
#         "price_per_km": 0.16,
#         "dep_hours": list(range(6, 22)),
#         "transfers_pool": [0],             # Direct connections
#     },
#     "CostaLink": {
#         "description": "Strong coverage of coastal destinations",
#         "speed_kmh": 78.0,
#         "price_per_km": 0.12,
#         "dep_hours": list(range(7, 21)),
#         "transfers_pool": [0, 1],
#     },
#     "VerdeBus": {
#         "description": "Environment-focused services and modern vehicles",
#         "speed_kmh": 80.0,
#         "price_per_km": 0.13,
#         "dep_hours": list(range(7, 21)),
#         "transfers_pool": [0, 1],
#     },
#     "NocheVia": {
#         "description": "Overnight and late-evening services",
#         "speed_kmh": 79.0,
#         "price_per_km": 0.11,
#         "dep_hours": [20, 21, 22, 23, 0],  # Late-evening & overnight departures
#         "transfers_pool": [0, 1],
#     },
# }


# def calculate_duration_minutes(destination: str, company: str, transfers: int, transfer_delay: int = 30) -> int:
#     """Distance-speed-time formula: time (hours) = distance / speed, converted to minutes + transfer stops."""
#     distance_km = MADRID_DISTANCES.get(destination.strip().lower(), 420)
#     profile = COMPANY_PROFILES.get(company.strip(), {})
#     base_speed = profile.get("speed_kmh", 78.0)
#     speed_kmh = max(60.0, base_speed + random.uniform(-3.0, 3.0))

#     driving_minutes = round((distance_km / speed_kmh) * 60)
#     transfer_minutes = max(0, transfers) * transfer_delay
#     return max(30, driving_minutes + transfer_minutes)


# def calculate_arrival_time(date_str: str, departure_time: str, duration_minutes: int) -> str:
#     """Adds exact duration_minutes to departure_time (handles past-midnight arrivals cleanly)."""
#     dep_dt = datetime.strptime(f"{date_str} {departure_time}", "%Y-%m-%d %H:%M")
#     arr_dt = dep_dt + timedelta(minutes=duration_minutes)
#     return arr_dt.strftime("%H:%M")


# def generate_full_year_offers(output_filepath=os.path.join(DATA_DIR, "offers.csv")):
#     log_event("Generating offers for SolRuta, Camino Express, CostaLink, VerdeBus, and NocheVia...")

#     dest_filepath = os.path.join(DATA_DIR, "destination.csv")
#     destinations = []
#     if os.path.exists(dest_filepath):
#         with open(dest_filepath, mode="r", encoding="utf-8") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 name = row.get("name", "").strip()
#                 if name and name.lower() != "madrid":
#                     destinations.append(name)

#     if not destinations:
#         destinations = [name.title() for name in MADRID_DISTANCES.keys()]

#     start_date = datetime.now()
#     offers = []

#     for day_offset in range(365):
#         date_str = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")

#         for dest in destinations:
#             distance_km = MADRID_DISTANCES.get(dest.lower(), 420)

#             for company, cfg in COMPANY_PROFILES.items():
#                 for _ in range(3):
#                     dep_hour = random.choice(cfg["dep_hours"])
#                     dep_minute = random.choice([0, 15, 30, 45])
#                     departure_time = f"{dep_hour:02d}:{dep_minute:02d}"

#                     transfers = random.choice(cfg["transfers_pool"])
#                     duration_minutes = calculate_duration_minutes(dest, company, transfers)
#                     arrival_time = calculate_arrival_time(date_str, departure_time, duration_minutes)

#                     base_price = distance_km * cfg["price_per_km"]
#                     price = round(random.uniform(base_price * 0.85, base_price * 1.15), 2)

#                     luggage = True
#                     changeable = random.choice([True, False]) if company != "Camino Express" else True
#                     refundable = random.choice([True, False])
#                     seats = random.randint(10, 40)
#                     rating = round(random.uniform(4.1, 5.0), 1) if company in ("Camino Express", "VerdeBus") else round(random.uniform(3.5, 4.7), 1)

#                     offers.append([
#                         company, dest, date_str, departure_time, arrival_time,
#                         duration_minutes, price, transfers, luggage, changeable, refundable, seats, rating
#                     ])

#     os.makedirs(DATA_DIR, exist_ok=True)
#     header = [
#         "company", "destination", "date", "departure_time", "arrival_time",
#         "duration", "price", "transfers", "luggage", "changeable", "refundable", "seats", "rating"
#     ]

#     with open(output_filepath, mode="w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(header)
#         writer.writerows(offers)

#     log_event(f"Generated {len(offers)} realistic offers in {output_filepath}")


# def load_destinations(filepath=os.path.join(DATA_DIR, "destination.csv")):
#     destinations = []
#     if os.path.exists(filepath):
#         with open(filepath, mode="r", encoding="utf-8") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 name = row.get("name", "").strip()
#                 if not name or name.lower() == "madrid":
#                     continue
#                 try:
#                     region = int(row.get("region", 0))
#                     destinations.append(Destination(name=name, region=region))
#                 except Exception as e:
#                     log_rejection(str(row), f"Invalid destination record: {e}")
#     else:
#         fallback_names = list(MADRID_DISTANCES.keys())
#         destinations = [Destination(name=name.title(), region=i + 1) for i, name in enumerate(fallback_names)]
#         log_event("destination.csv not found. Loaded default destinations (excluding Madrid).")
#     return destinations


# def load_offers(filepath=os.path.join(DATA_DIR, "offers.csv")):
#     if not os.path.exists(filepath):
#         generate_full_year_offers(output_filepath=filepath)

#     valid_destinations = {d.name.lower() for d in load_destinations()}
#     offers = []
#     rejected_count = 0

#     with open(filepath, mode="r", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             try:
#                 required_fields = [
#                     "company", "destination", "date", "departure_time",
#                     "arrival_time", "duration", "price", "seats"
#                 ]
#                 if any(not row.get(field) for field in required_fields):
#                     raise ValueError("Missing required field values.")

#                 company = row["company"].strip()
#                 destination = row["destination"].strip()

#                 if destination.lower() not in valid_destinations:
#                     raise ValueError(f"Unknown destination '{destination}'.")

#                 date_str = row["date"].strip()
#                 if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
#                     raise ValueError(f"Invalid date format '{date_str}'.")
#                 datetime.strptime(date_str, "%Y-%m-%d")

#                 price = float(row["price"])
#                 if price < 0:
#                     raise ValueError(f"Negative price (€{price}).")

#                 duration = int(row["duration"])
#                 if duration <= 0:
#                     raise ValueError(f"Non-positive duration ({duration} mins).")

#                 seats = int(row["seats"])
#                 if seats < 0:
#                     raise ValueError(f"Negative seat count ({seats}).")

#                 dep_time = row["departure_time"].strip()
#                 arr_time = row["arrival_time"].strip()

#                 expected_arr_time = calculate_arrival_time(date_str, dep_time, duration)
#                 if arr_time != expected_arr_time:
#                     raise ValueError(
#                         f"Arrival time '{arr_time}' does not match '{dep_time}' + {duration}m (expected '{expected_arr_time}')."
#                     )

#                 rating = float(row.get("rating", 4.0))
#                 rating = max(1.0, min(5.0, rating))

#                 offers.append(Offer(
#                     company=company,
#                     destination=destination,
#                     date=date_str,
#                     departure_time=dep_time,
#                     arrival_time=arr_time,
#                     duration=duration,
#                     price=price,
#                     transfers=int(row.get("transfers", 0)),
#                     luggage=str(row.get("luggage", True)).lower() == "true",
#                     changeable=str(row.get("changeable", False)).lower() == "true",
#                     refundable=str(row.get("refundable", False)).lower() == "true",
#                     seats=seats,
#                     rating=rating
#                 ))
#             except Exception as e:
#                 rejected_count += 1
#                 log_rejection(str(row), str(e))

#     log_event(f"Loaded {len(offers)} valid offers; rejected {rejected_count} invalid offers.")
#     return offers


# def load_sample_data():
#     companies = [
#         Company(name=name, profile=cfg["description"])
#         for name, cfg in COMPANY_PROFILES.items()
#     ]
#     destinations = load_destinations()
#     offers = load_offers()
#     return companies, destinations, offers

import csv
import os
import random
import re
from datetime import datetime, timedelta
from typing import List, Optional
from models import Destination, Offer, Company
from custom_logger import log_event, log_rejection

DATA_DIR = os.path.join(os.getcwd(), "data")

MADRID_DISTANCES = {
    "barcelona": 620,
    "valencia": 355,
    "seville": 530,
    "malaga": 530,
    "granada": 420,
    "cordoba": 400,
    "bilbao": 400,
    "san sebastian": 460,
    "zaragoza": 320,
    "alicante": 420,
    "murcia": 400,
    "salamanca": 215,
    "toledo": 75,
    "santiago de compostela": 600,
    "cadiz": 650,
}

COMPANY_PROFILES = {
    "SolRuta": {
        "description": "Low-cost daytime services",
        "speed_kmh": 75.0,
        "price_per_km": 0.09,
        "dep_hours": list(range(7, 18)),
        "transfers_pool": [0, 1, 2],
    },
    "Camino Express": {
        "description": "Fast direct connections between major cities",
        "speed_kmh": 85.0,
        "price_per_km": 0.16,
        "dep_hours": list(range(6, 22)),
        "transfers_pool": [0],
    },
    "CostaLink": {
        "description": "Strong coverage of coastal destinations",
        "speed_kmh": 78.0,
        "price_per_km": 0.12,
        "dep_hours": list(range(7, 21)),
        "transfers_pool": [0, 1],
    },
    "VerdeBus": {
        "description": "Environment-focused services and modern vehicles",
        "speed_kmh": 80.0,
        "price_per_km": 0.13,
        "dep_hours": list(range(7, 21)),
        "transfers_pool": [0, 1],
    },
    "NocheVia": {
        "description": "Overnight and late-evening services",
        "speed_kmh": 79.0,
        "price_per_km": 0.11,
        "dep_hours": [20, 21, 22, 23, 0],
        "transfers_pool": [0, 1],
    },
}


def calculate_duration_minutes(destination: str, company: str, transfers: int, transfer_delay: int = 30) -> int:
    """Distance-speed-time formula: time (hours) = distance / speed, converted to minutes + transfer stops."""
    distance_km = MADRID_DISTANCES.get(destination.strip().lower(), 420)
    profile = COMPANY_PROFILES.get(company.strip(), {})
    base_speed = profile.get("speed_kmh", 78.0)
    speed_kmh = max(60.0, base_speed + random.uniform(-3.0, 3.0))

    driving_minutes = round((distance_km / speed_kmh) * 60)
    transfer_minutes = max(0, transfers) * transfer_delay
    return max(30, driving_minutes + transfer_minutes)


def calculate_arrival_time(date_str: str, departure_time: str, duration_minutes: int) -> str:
    """Adds exact duration_minutes to departure_time (handles past-midnight arrivals cleanly)."""
    dep_dt = datetime.strptime(f"{date_str} {departure_time}", "%Y-%m-%d %H:%M")
    arr_dt = dep_dt + timedelta(minutes=duration_minutes)
    return arr_dt.strftime("%H:%M")


def _inject_offer_anomaly(row: list, anomaly_type: str) -> list:
    """Mutates a valid offer row into an invalid anomaly to test validation and rejection logging."""
    mutated = list(row)
    if anomaly_type == "negative_price":
        mutated[6] = -15.00
    elif anomaly_type == "invalid_duration":
        mutated[5] = 0
    elif anomaly_type == "negative_seats":
        mutated[11] = -3
    elif anomaly_type == "unknown_destination":
        mutated[1] = "UnknownCity"
    elif anomaly_type == "mismatched_arrival":
        mutated[4] = "25:99"
    elif anomaly_type == "invalid_date":
        mutated[2] = "2026-99-99"
    return mutated


def generate_full_year_offers(
    output_filepath: str = os.path.join(DATA_DIR, "offers.csv"),
    anomaly_rate: float = 0.01,
) -> None:
    log_event(
        f"Generating offers using distance-speed-time formula (anomaly_rate={anomaly_rate:.2%})..."
    )

    dest_filepath = os.path.join(DATA_DIR, "destination.csv")
    destinations = []
    if os.path.exists(dest_filepath):
        with open(dest_filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "").strip()
                if name and name.lower() != "madrid":
                    destinations.append(name)

    if not destinations:
        destinations = [name.title() for name in MADRID_DISTANCES.keys()]

    start_date = datetime.now()
    offers = []
    injected_count = 0
    anomaly_types = [
        "negative_price",
        "invalid_duration",
        "negative_seats",
        "unknown_destination",
        "mismatched_arrival",
        "invalid_date",
    ]

    for day_offset in range(365):
        date_str = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")

        for dest in destinations:
            distance_km = MADRID_DISTANCES.get(dest.lower(), 420)

            for company, cfg in COMPANY_PROFILES.items():
                for _ in range(3):
                    dep_hour = random.choice(cfg["dep_hours"])
                    dep_minute = random.choice([0, 15, 30, 45])
                    departure_time = f"{dep_hour:02d}:{dep_minute:02d}"

                    transfers = random.choice(cfg["transfers_pool"])
                    duration_minutes = calculate_duration_minutes(dest, company, transfers)
                    arrival_time = calculate_arrival_time(date_str, departure_time, duration_minutes)

                    base_price = distance_km * cfg["price_per_km"]
                    price = round(random.uniform(base_price * 0.85, base_price * 1.15), 2)

                    luggage = True
                    changeable = random.choice([True, False]) if company != "Camino Express" else True
                    refundable = random.choice([True, False])
                    seats = random.randint(10, 40)
                    rating = (
                        round(random.uniform(4.1, 5.0), 1)
                        if company in ("Camino Express", "VerdeBus")
                        else round(random.uniform(3.5, 4.7), 1)
                    )

                    row = [
                        company, dest, date_str, departure_time, arrival_time,
                        duration_minutes, price, transfers, luggage, changeable,
                        refundable, seats, rating
                    ]

                    if anomaly_rate > 0 and random.random() < anomaly_rate:
                        chosen_anomaly = random.choice(anomaly_types)
                        row = _inject_offer_anomaly(row, chosen_anomaly)
                        injected_count += 1

                    offers.append(row)

    os.makedirs(DATA_DIR, exist_ok=True)
    header = [
        "company", "destination", "date", "departure_time", "arrival_time",
        "duration", "price", "transfers", "luggage", "changeable", "refundable", "seats", "rating"
    ]

    with open(output_filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(offers)

    log_event(
        f"Generated {len(offers)} offers ({injected_count} intentional anomalies injected) in {output_filepath}"
    )


def load_destinations(filepath: str = os.path.join(DATA_DIR, "destination.csv")) -> List[Destination]:
    destinations = []
    if os.path.exists(filepath):
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "").strip()
                if not name or name.lower() == "madrid":
                    continue
                try:
                    region = int(row.get("region", 0))
                    destinations.append(Destination(name=name, region=region))
                except Exception as e:
                    log_rejection(str(row), f"Invalid destination record: {e}")
    else:
        fallback_names = list(MADRID_DISTANCES.keys())
        destinations = [Destination(name=name.title(), region=i + 1) for i, name in enumerate(fallback_names)]
        log_event("destination.csv not found. Loaded default destinations (excluding Madrid).")
    return destinations


def load_offers(filepath: str = os.path.join(DATA_DIR, "offers.csv")) -> List[Offer]:
    if not os.path.exists(filepath):
        generate_full_year_offers(output_filepath=filepath)

    valid_destinations = {d.name.lower() for d in load_destinations()}
    offers = []
    rejected_count = 0

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                required_fields = [
                    "company", "destination", "date", "departure_time",
                    "arrival_time", "duration", "price", "seats"
                ]
                if any(not row.get(field) for field in required_fields):
                    raise ValueError("Missing required field values.")

                company = row["company"].strip()
                destination = row["destination"].strip()

                if destination.lower() not in valid_destinations:
                    raise ValueError(f"Unknown destination '{destination}'.")

                date_str = row["date"].strip()
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
                    raise ValueError(f"Invalid date format '{date_str}'.")
                datetime.strptime(date_str, "%Y-%m-%d")

                price = float(row["price"])
                if price < 0:
                    raise ValueError(f"Negative price (€{price}).")

                duration = int(row["duration"])
                if duration <= 0:
                    raise ValueError(f"Non-positive duration ({duration} mins).")

                seats = int(row["seats"])
                if seats < 0:
                    raise ValueError(f"Negative seat count ({seats}).")

                dep_time = row["departure_time"].strip()
                arr_time = row["arrival_time"].strip()

                expected_arr_time = calculate_arrival_time(date_str, dep_time, duration)
                if arr_time != expected_arr_time:
                    raise ValueError(
                        f"Arrival time '{arr_time}' does not match '{dep_time}' + {duration}m (expected '{expected_arr_time}')."
                    )

                rating = float(row.get("rating", 4.0))
                rating = max(1.0, min(5.0, rating))

                offers.append(Offer(
                    company=company,
                    destination=destination,
                    date=date_str,
                    departure_time=dep_time,
                    arrival_time=arr_time,
                    duration=duration,
                    price=price,
                    transfers=int(row.get("transfers", 0)),
                    luggage=str(row.get("luggage", True)).lower() == "true",
                    changeable=str(row.get("changeable", False)).lower() == "true",
                    refundable=str(row.get("refundable", False)).lower() == "true",
                    seats=seats,
                    rating=rating
                ))
            except Exception as e:
                rejected_count += 1
                log_rejection(str(row), str(e))

    log_event(f"Loaded {len(offers)} valid offers; rejected {rejected_count} invalid offers.")
    return offers


def load_sample_data(filepath: Optional[str] = None):
    companies = [
        Company(name=name, profile=cfg["description"])
        for name, cfg in COMPANY_PROFILES.items()
    ]
    destinations = load_destinations()
    offers = load_offers(filepath) if filepath else load_offers()
    return companies, destinations, offers