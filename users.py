import csv
import os
import random
import re




from custom_logger import log_event




CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")

# def register_user(name: str, email: str, phone: str, traveller_type: str) -> str:
#     """
#     Generates a unique User ID based on traveller type, 
#     persists user details to data/users.csv, and returns the User ID.
#     """
#     os.makedirs(DATA_DIR, exist_ok=True)
    
#     # Unique ID prefix based on traveller profile type
#     prefix_map = {
#         "business": "BIZ",
#         "economical": "ECO",
#         "environment_friendly": "ENV",
#         "flexible": "FLX"
#     }
#     prefix = prefix_map.get(traveller_type.lower(), "USR")
#     random_digits = random.randint(1000, 9999)
#     user_id = f"{prefix}-{random_digits}"

#     file_exists = os.path.exists(USERS_FILE)
#     with open(USERS_FILE, mode="a", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         if not file_exists:
#             writer.writerow(["user_id", "name", "email", "phone", "traveller_type"])
#         writer.writerow([user_id, name, email, phone, traveller_type])

#     print(f"👤 User registered successfully! Assigned User ID: {user_id} (Saved to data/users.csv)")
#     return user_id




def validate_user_id(user_id: str) -> bool:
    """Validates structured user identifiers using regex (e.g., BIZ-1234, ECO-5678)."""
    pattern = r"^(BIZ|ECO|ENV|FLX)-\d{4}$"
    return bool(re.match(pattern, user_id))



DATA_DIR = os.path.join(os.getcwd(), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")

def register_user(name: str, email: str, phone: str, traveller_type: str) -> str:
    """
    Generates a unique User ID based on traveller type, 
    persists user details to data/users.csv, and returns the User ID.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    prefix_map = {
        "business": "BIZ",
        "economical": "ECO",
        "environment_friendly": "ENV",
        "flexible": "FLX"
    }
    prefix = prefix_map.get(traveller_type.lower(), "USR")
    random_digits = random.randint(1000, 9999)
    user_id = f"{prefix}-{random_digits}"

    file_exists = os.path.exists(USERS_FILE)
    with open(USERS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user_id", "name", "email", "phone", "traveller_type"])
        writer.writerow([user_id, name, email, phone, traveller_type])

    msg = f"User registered successfully! Assigned User ID: {user_id}, Name: {name}, Type: {traveller_type}"
    print(f"👤 {msg} (Saved to {USERS_FILE})")
    log_event(msg)
    return user_id