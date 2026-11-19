import re
from datetime import datetime
from typing import Dict, List, Optional
from loader import load_sample_data
from models import TravellerProfile
from filtering import filter_offers
from ranking import RankingEngine
from validators import validate_weights, WeightValidationError
from booking import book_offer_for_group
from users import register_user
from credits import get_user_credit, update_user_credit, redeem_voucher
from custom_logger import log_event
from profile_registry import TravellerProfileRegistry


def _prompt_int(prompt: str, default: int, min_val: Optional[int] = None) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw:
            val = default
        else:
            try:
                val = int(raw)
            except ValueError:
                print("❌ Please enter a valid whole number.")
                continue
        if min_val is not None and val < min_val:
            print(f"❌ Value must be at least {min_val}.")
            continue
        return val


def _prompt_float(prompt: str, default: float, min_val: Optional[float] = None) -> float:
    while True:
        raw = input(prompt).strip()
        if not raw:
            val = default
        else:
            try:
                val = float(raw)
            except ValueError:
                print("❌ Please enter a valid number.")
                continue
        if min_val is not None and val < min_val:
            print(f"❌ Value must be at least {min_val}.")
            continue
        return val


def _format_flex(offer) -> str:
    c = "C" if getattr(offer, "changeable", False) else "-"
    r = "R" if getattr(offer, "refundable", False) else "-"
    return f"{c}/{r}"


def _print_ranked_table(detailed_results: List[dict], limit: int = 15) -> None:
    print("=" * 130)
    print(
        f"{'Rank':<4} | {'Company':<10} | {'Date':<10} | {'Dep->Arr':<11} | {'Dur(h)':<6} | "
        f"{'Trf':<3} | {'Flex':<4} | {'Seats':<5} | {'Price':<7} | "
        f"{'P_Sc':<5} | {'D_Sc':<5} | {'T_Sc':<5} | {'F_Sc':<5} | {'Total'}"
    )
    print("=" * 130)
    print("Legend -> Flex: C=Changeable, R=Refundable | Scores (0-100): P=Price, D=Duration, T=Departure Time, F=Flexibility")
    print("-" * 130)

    for idx, item in enumerate(detailed_results[:limit], start=1):
        o = item["offer"]
        v = item["values"]
        sc = item["scores"]
        dep_arr = f"{o.departure_time}->{o.arrival_time}"
        print(
            f"#{idx:<3} | {o.company:<10} | {o.date:<10} | {dep_arr:<11} | "
            f"{v['duration']/60:<6.2f} | {v['transfers']:<3} | {_format_flex(o):<4} | "
            f"{o.seats:<5} | €{v['price']:<6.2f} | "
            f"{sc['price']:<5.1f} | {sc['duration']:<5.1f} | {sc['time']:<5.1f} | "
            f"{sc['flexibility']:<5.1f} | {item['total_score']:>5.2f}"
        )
    print("=" * 130)


def _run_multi_profile_comparison(all_offers: list, destinations: list) -> None:
    print("\n" + "=" * 75)
    print("📊 MULTI-PROFILE COMPARISON ON IDENTICAL OFFER SET")
    print("=" * 75)

    for idx, d in enumerate(destinations, 1):
        print(f"  {idx:2d}. {d.name}")

    while True:
        dest_idx = _prompt_int(f"Select destination number [1-{len(destinations)}]: ", default=1, min_val=1)
        if dest_idx <= len(destinations):
            selected_destination = destinations[dest_idx - 1].name
            break
        print(f"❌ Enter a number between 1 and {len(destinations)}.")

    default_date = datetime.now().strftime("%Y-%m-%d")
    start_date = input(f"Travel Start Date (YYYY-MM-DD) [Default: {default_date}]: ").strip() or default_date
    end_date = input(f"Travel End Date (YYYY-MM-DD) [Default: {start_date}]: ").strip() or start_date
    min_seats = _prompt_int("Seats Required [Default: 1]: ", default=1, min_val=1)

    base_pool = [
        o for o in all_offers
        if o.destination.strip().lower() == selected_destination.strip().lower()
        and start_date <= o.date <= end_date
        and o.seats >= min_seats
        and getattr(o, "luggage", True)
    ]

    if not base_pool:
        print(f"⚠️ No offers found for {selected_destination} between {start_date} and {end_date} with {min_seats} seat(s).")
        return

    print(f"\nComparing across {len(base_pool)} matching base offers for {selected_destination} ({start_date} to {end_date}):\n")

    for key, spec in TravellerProfileRegistry.all_profiles():
        validate_weights(spec.weights)
        prof = TravellerProfile(
            origin="Madrid",
            destination=selected_destination,
            travel_window=(start_date, end_date),
            max_budget=spec.max_budget,
            min_seats=min_seats,
            max_transfers=spec.max_transfers,
            require_luggage=True,
            max_duration=spec.max_duration,
            require_changeable=spec.require_changeable,
            preferred_time=spec.preferred_time,
            weights=dict(spec.weights),
        )
        eligible = filter_offers(base_pool, prof)
        detailed = RankingEngine.score_offers_detailed(eligible, prof)

        print("-" * 75)
        print(f"Profile [{key}]: {spec.label} | Weights: {spec.weights} | Eligible Offers: {len(eligible)}")
        if not detailed:
            print("  No offers satisfied this profile's mandatory constraints.")
            continue

        top_3 = ", ".join(
            f"#{i} {d['offer'].company} ({d['offer'].departure_time}->{d['offer'].arrival_time}, €{d['values']['price']:.2f}, {d['total_score']:.1f})"
            for i, d in enumerate(detailed[:3], start=1)
        )
        print(f"  Top 3 Ranking: {top_3}")
        explanation = RankingEngine.generate_top_explanation(detailed[0], detailed, prof, profile_label=spec.label)
        print(explanation)

    log_event(f"Completed multi-profile comparison for {selected_destination} ({start_date} to {end_date}).")


def main() -> None:
    log_event("BusBidder application session started.")
    print("=" * 75)
    print("🌊 Welcome to BusBidder Spain (Terminal Edition) 🌊")
    print("=" * 75)

    companies, destinations, all_offers = load_sample_data()

    # 1. Traveller Profile & Type Selection (dynamically discovered via TravellerProfileRegistry)
    print("\n--- Step 1: Traveller Profile & Type Selection ---")
    registered = TravellerProfileRegistry.all_profiles()
    for key, spec in registered:
        print(f"{key}. {spec.label} (Type: {spec.traveller_type})")
    print("5. Custom Traveller (Create with strict regex validation)")
    print("6. Compare All Profiles on Same Offers (Side-by-side ranking demonstration)")

    choice = input("Select profile option [1-6, Default: 2]: ").strip() or "2"

    if choice == "6":
        _run_multi_profile_comparison(all_offers, destinations)
        return

    preferred_time = "Morning"
    selected_spec = TravellerProfileRegistry.get(choice)

    if selected_spec is not None and choice != "5":
        name_input = selected_spec.name
        email_input = selected_spec.email
        phone_input = selected_spec.phone
        traveller_type = selected_spec.traveller_type
        max_bud = selected_spec.max_budget
        max_trans = selected_spec.max_transfers
        max_dur = selected_spec.max_duration
        req_change = selected_spec.require_changeable
        preferred_time = selected_spec.preferred_time
        weights: Dict[str, float] = dict(selected_spec.weights)
        profile_label = selected_spec.label
    else:
        profile_label = "Custom Traveller"
        print("\n--- Register Custom Traveller ---")
        while True:
            name_input = input("Enter Name (letters/spaces only, 2-40 chars): ").strip()
            if re.match(r"^[A-Za-zÀ-ÿ\s]{2,40}$", name_input):
                break
            print("❌ Invalid Name format. Letters and spaces only (no numbers/symbols).")

        while True:
            email_input = input("Enter Email (e.g., user@gmail.com): ").strip()
            if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_input):
                break
            print("❌ Invalid Email format. Please try again.")

        while True:
            phone_input = input("Enter Spanish Phone Number (9 digits, optional +34): ").strip()
            if re.match(r"^(\+34|0034)?[6-9]\d{8}$", phone_input):
                break
            print("❌ Invalid Spanish phone format (must be 9 digits starting with 6-9).")

        print("Select Traveller Type: 1. business | 2. economical | 3. environment_friendly | 4. flexible")
        t_choice = input("Enter choice [1-4, Default: 2]: ").strip()
        type_map = {"1": "business", "2": "economical", "3": "environment_friendly", "4": "flexible"}
        traveller_type = type_map.get(t_choice, "economical")

        max_bud = _prompt_float("Maximum Budget in € [Default: 100.0]: ", default=100.0, min_val=0.0)
        max_trans = _prompt_int("Maximum Transfers Allowed [Default: 2]: ", default=2, min_val=0)
        max_dur_hours = _prompt_float("Maximum Duration in hours [Default: 9.0]: ", default=9.0, min_val=0.5)
        max_dur = int(round(max_dur_hours * 60))
        req_change = input("Require Changeable Ticket? (y/n) [Default: n]: ").strip().lower() == "y"
        preferred_time = input("Preferred Departure Window (Morning/Afternoon/Evening/Night) [Default: Morning]: ").strip() or "Morning"
        weights = {"price": 0.40, "duration": 0.25, "time": 0.15, "flexibility": 0.20}

    log_event(f"User selected profile choice [{choice}], Traveller Type: [{traveller_type}], Name: [{name_input}]")
    user_id = register_user(name_input, email_input, phone_input, traveller_type)

    current_credits = get_user_credit(user_id)
    print(f"\n💳 Available Travel Credit Balance: €{current_credits:.2f}")

    has_voucher = input("Do you have a promotional voucher code? (y/n): ").strip().lower()
    if has_voucher == "y":
        v_code = input("Enter Voucher Code (e.g., SPAIN2026, BUSBUD50): ").strip()
        bonus = redeem_voucher(v_code)
        if bonus > 0:
            current_credits += bonus
            update_user_credit(user_id, current_credits)
            print(f"🎉 Voucher applied successfully! New Credit Balance: €{current_credits:.2f}")
        else:
            print("❌ Invalid or expired voucher code.")

    # 2. HARD CONSTRAINTS (Mandatory Filters)
    print("\n" + "=" * 75)
    print(f"🛑 STEP 2: MANDATORY HARD CONSTRAINTS [Profile: {profile_label}]")
    print("=" * 75)

    print(f"Available Destinations ({len(destinations)}):")
    for idx, d in enumerate(destinations, 1):
        print(f"  {idx:2d}. {d.name}")

    while True:
        dest_idx = _prompt_int(f"Select destination number [1-{len(destinations)}]: ", default=1, min_val=1)
        if dest_idx <= len(destinations):
            selected_destination = destinations[dest_idx - 1].name
            break
        print(f"❌ Enter a number between 1 and {len(destinations)}.")

    default_date = datetime.now().strftime("%Y-%m-%d")
    start_date = input(f"Travel Start Date (YYYY-MM-DD) [Default: {default_date}]: ").strip() or default_date
    end_date = input(f"Travel End Date (YYYY-MM-DD) [Default: {start_date}]: ").strip() or start_date
    min_seats = _prompt_int("Seats Required [Default: 1]: ", default=1, min_val=1)

    additional_travellers = []
    if min_seats > 1:
        print(f"\n--- Enter details for the remaining {min_seats - 1} additional passenger(s) ---")
        for i in range(2, min_seats + 1):
            print(f"\nPassenger #{i}:")
            while True:
                add_name = input("  Enter Name: ").strip()
                if re.match(r"^[A-Za-zÀ-ÿ\s]{2,40}$", add_name):
                    break
                print("  ❌ Invalid Name format.")

            add_gender = input("  Enter Gender (e.g., Male, Female, Other): ").strip() or "Not Specified"

            while True:
                add_email = input("  Enter Email: ").strip()
                if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", add_email):
                    break
                print("  ❌ Invalid Email format.")

            while True:
                add_phone = input("  Enter Phone (9 digits): ").strip()
                if re.match(r"^(\+34|0034)?[6-9]\d{8}$", add_phone):
                    break
                print("  ❌ Invalid phone format.")

            additional_travellers.append({
                "name": add_name,
                "gender": add_gender,
                "email": add_email,
                "phone": add_phone,
            })

    log_event(f"Search parameters set -> Destination: {selected_destination}, Window: {start_date} to {end_date}, Seats: {min_seats}")

    # 3. WEIGHT VALIDATION & PROFILE CREATION
    try:
        validate_weights(weights)
    except WeightValidationError as e:
        print(f"❌ Weight validation failed: {e}")
        return

    profile = TravellerProfile(
        origin="Madrid",
        destination=selected_destination,
        travel_window=(start_date, end_date),
        max_budget=max_bud,
        min_seats=min_seats,
        max_transfers=max_trans,
        require_luggage=True,
        max_duration=max_dur,
        require_changeable=req_change,
        preferred_time=preferred_time,
        weights=weights,
    )

    # 4. Filter & Rank Execution
    print("\n🔍 Filtering hard constraints and ranking matching offers...")
    filtered_offers = filter_offers(all_offers, profile)
    detailed_results = RankingEngine.score_offers_detailed(filtered_offers, profile)

    print(f"\n🎉 {len(filtered_offers)} offers passed all hard constraints for {selected_destination}!\n")
    log_event(f"Found {len(filtered_offers)} offers passing hard constraints for {selected_destination}")

    if not detailed_results:
        print("⚠️ No offers matched your mandatory constraints. Try relaxing your budget or date window.")
        return

    _print_ranked_table(detailed_results, limit=15)

    top_explanation = RankingEngine.generate_top_explanation(
        detailed_results[0], detailed_results, profile, profile_label=profile_label
    )
    print("\n" + top_explanation + "\n")

    # 5. Interactive Booking Workflow with Travel Credits
    book_choice = input("Would you like to book one of these offers? (y/n): ").strip().lower()
    if book_choice == "y":
        try:
            offer_num = _prompt_int("Enter the Rank number you wish to book: ", default=1, min_val=1)
            if 1 <= offer_num <= len(detailed_results):
                chosen_offer = detailed_results[offer_num - 1]["offer"]

                total_ticket_price = chosen_offer.price * min_seats
                use_credits = 0.0
                if current_credits > 0:
                    print(f"\nYou have €{current_credits:.2f} in travel credits available.")
                    use_credits_choice = input(
                        f"Would you like to apply your credits to this booking (Total: €{total_ticket_price:.2f})? (y/n): "
                    ).strip().lower()
                    if use_credits_choice == "y":
                        max_possible = min(current_credits, total_ticket_price)
                        use_credits = _prompt_float(
                            f"Enter amount to apply [Max: €{max_possible:.2f}, Default: {max_possible:.2f}]: ",
                            default=max_possible,
                            min_val=0.0,
                        )
                        use_credits = min(use_credits, max_possible)

                book_offer_for_group(
                    chosen_offer,
                    profile,
                    primary_name=name_input,
                    primary_email=email_input,
                    primary_phone=phone_input,
                    additional_travellers=additional_travellers,
                    user_id=user_id,
                    use_credits=use_credits,
                )
                print(f"🎟️ Booking complete for User ID: {user_id}! Saved to data/bookings.csv.")
            else:
                print("❌ Invalid rank selection.")
        except Exception as err:
            print(f"❌ Booking failed: {err}")
            log_event(f"Booking failed: {err}", level="ERROR")


if __name__ == "__main__":
    main()