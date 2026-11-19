import csv
import os
from custom_logger import log_event
from credits import get_user_credit, update_user_credit

DATA_DIR = os.path.join(os.getcwd(), "data")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.csv")
OFFERS_FILE = os.path.join(DATA_DIR, "offers.csv")

def update_offer_seats_in_csv(booked_offer, seats_booked: int):
    """Decrements the seat count for the matching offer in data/offers.csv."""
    if not os.path.exists(OFFERS_FILE):
        return

    rows = []
    updated = False
    with open(OFFERS_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if (not updated and
                row["company"] == booked_offer.company and
                row["destination"] == booked_offer.destination and
                row["date"] == booked_offer.date and
                row["departure_time"] == booked_offer.departure_time and
                float(row["price"]) == booked_offer.price):
                row["seats"] = str(max(0, int(row["seats"]) - seats_booked))
                updated = True
            rows.append(row)

    if updated and fieldnames:
        with open(OFFERS_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

def book_offer_for_group(offer, profile, primary_name: str, primary_email: str, primary_phone: str, additional_travellers: list, user_id: str, use_credits: float = 0.0):
    """
    Validates seats, deducts travel credits, updates offers.csv, 
    and records booking details into data/bookings.csv.
    """
    seats_needed = profile.min_seats
    if offer.seats < seats_needed:
        raise ValueError(f"Only {offer.seats} seats available, but {seats_needed} requested.")
    
    total_price = offer.price * seats_needed
    final_price = max(0.0, total_price - use_credits)

    # Deduct credits from user's balance if used
    if use_credits > 0:
        current_bal = get_user_credit(user_id)
        new_bal = max(0.0, current_bal - use_credits)
        update_user_credit(user_id, new_bal)

    # 1. Update in-memory offer and offers.csv
    offer.seats -= seats_needed
    update_offer_seats_in_csv(offer, seats_needed)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.exists(BOOKINGS_FILE)
    
    all_travellers = [{"name": primary_name, "email": primary_email, "phone": primary_phone, "gender": "Not Specified"}] + additional_travellers
    
    with open(BOOKINGS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "user_id", "traveller_name", "gender", "email", "phone", "company", 
                "destination", "date", "departure_time", "total_price_eur", "credits_used_eur", "final_paid_eur"
            ])
        
        for t in all_travellers:
            writer.writerow([
                user_id,
                t["name"],
                t.get("gender", "N/A"),
                t["email"],
                t["phone"],
                offer.company,
                offer.destination,
                offer.date,
                offer.departure_time,
                f"{total_price:.2f}",
                f"{use_credits:.2f}",
                f"{final_price:.2f}"
            ])
        
    conf_msg = f"Group Booking Confirmed (User: {user_id}) -> Seats: {seats_needed}, Destination: {offer.destination}, Total: €{total_price:.2f}, Credits Applied: €{use_credits:.2f}, Final Paid: €{final_price:.2f}"
    print(f"🎟️ Successfully booked! Total: €{total_price:.2f} | Credits Applied: -€{use_credits:.2f} | Final Paid: €{final_price:.2f}")
    log_event(conf_msg)
    return True