import csv
import os
from custom_logger import log_event

DATA_DIR = os.path.join(os.getcwd(), "data")
CREDITS_FILE = os.path.join(DATA_DIR, "credits.csv")

def get_user_credit(user_id: str) -> float:
    """Retrieves available travel credit balance for a given User ID."""
    if not os.path.exists(CREDITS_FILE):
        # Initialize default credit for new users (€25.00 welcoming bonus)
        return 25.00
    
    with open(CREDITS_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["user_id"].strip().upper() == user_id.strip().upper():
                return float(row["balance_eur"])
    
    # Default if user ID not found in csv yet
    return 25.00

def update_user_credit(user_id: str, new_balance: float):
    """Updates or adds the user's credit balance in data/credits.csv."""
    os.makedirs(DATA_DIR, exist_ok=True)
    rows = []
    updated = False

    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row["user_id"].strip().upper() == user_id.strip().upper():
                    row["balance_eur"] = f"{new_balance:.2f}"
                    updated = True
                rows.append(row)
    else:
        fieldnames = ["user_id", "balance_eur"]

    if not updated:
        rows.append({"user_id": user_id, "balance_eur": f"{new_balance:.2f}"})

    with open(CREDITS_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def redeem_voucher(code: str) -> float:
    """Validates promotional voucher codes and returns credit value."""
    vouchers = {
        "SPAIN2026": 15.00,
        "BUSBUD50": 5.00,
        "WELCOME10": 10.00
    }
    code_clean = code.strip().upper()
    if code_clean in vouchers:
        val = vouchers[code_clean]
        log_event(f"Voucher redeemed successfully: {code_clean} (€{val:.2f})")
        return val
    return 0.0