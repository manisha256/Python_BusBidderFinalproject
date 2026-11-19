import csv
import os
import random
from datetime import datetime, timedelta
from loader import (
    MADRID_DISTANCES,
    COMPANY_PROFILES,
    calculate_duration_minutes,
    calculate_arrival_time,
    _inject_offer_anomaly,
)


def generate_offers_csv(
    dest_filepath: str = "data/destination.csv",
    output_filepath: str = "data/offers.csv",
    anomaly_rate: float = 0.02,
) -> None:
    destinations = []
    try:
        with open(dest_filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "").strip()
                if name and name.lower() != "madrid":
                    destinations.append(name)
    except FileNotFoundError:
        destinations = [name.title() for name in MADRID_DISTANCES.keys()]

    if not destinations:
        destinations = [name.title() for name in MADRID_DISTANCES.keys()]

    company_names = list(COMPANY_PROFILES.keys())
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

    for dest in destinations:
        distance_km = MADRID_DISTANCES.get(dest.lower(), 420)
        for _ in range(random.randint(8, 12)):
            company = random.choice(company_names)
            cfg = COMPANY_PROFILES[company]
            date = (start_date + timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d")

            dep_hour = random.choice(cfg["dep_hours"])
            dep_minute = random.choice([0, 15, 30, 45])
            departure_time = f"{dep_hour:02d}:{dep_minute:02d}"

            transfers = random.choice(cfg["transfers_pool"])
            duration = calculate_duration_minutes(dest, company, transfers)
            arrival_time = calculate_arrival_time(date, departure_time, duration)

            base_price = distance_km * cfg["price_per_km"]
            price = round(random.uniform(base_price * 0.85, base_price * 1.15), 2)

            luggage = True
            changeable = random.choice([True, False]) if company != "Camino Express" else True
            refundable = random.choice([True, False])
            seats = random.randint(5, 30)
            rating = (
                round(random.uniform(4.1, 5.0), 1)
                if company in ("Camino Express", "VerdeBus")
                else round(random.uniform(3.5, 4.7), 1)
            )

            row = [
                company, dest, date, departure_time, arrival_time,
                duration, price, transfers, luggage, changeable, refundable, seats, rating
            ]

            if anomaly_rate > 0 and random.random() < anomaly_rate:
                row = _inject_offer_anomaly(row, random.choice(anomaly_types))
                injected_count += 1

            offers.append(row)

    os.makedirs(os.path.dirname(output_filepath) or ".", exist_ok=True)
    header = [
        "company", "destination", "date", "departure_time", "arrival_time",
        "duration", "price", "transfers", "luggage", "changeable", "refundable", "seats", "rating"
    ]

    with open(output_filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(offers)

    print(
        f"✅ Generated {len(offers)} offers ({injected_count} anomalies) for "
        f"{', '.join(company_names)} in {output_filepath}!"
    )


if __name__ == "__main__":
    generate_offers_csv()