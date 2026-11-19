# BusBidder Spain

BusBidder Spain is a command-line intercity bus search, multi-criteria ranking, and simulated group-booking application developed for **ACIT4420**[cite: 5, 10]. It models routes originating from Madrid across 15 Spanish destination cities with five carriers (**SolRuta**, **Camino Express**, **CostaLink**, **VerdeBus**, and **NocheVia**)[cite: 8, 12], applies hard constraint filtering, ranks eligible offers using a weighted 0–100 scoring model, and records bookings, credits, and logs[cite: 1, 2, 4].

---

## Requirements & Environment

* **Python Version:** Python **3.8+** is supported (type annotations use `typing.Optional` / `typing.List` / `typing.Dict` rather than `|` union syntax for compatibility with Python 3.8 and 3.9).
* **Required Libraries:** Uses the **Python Standard Library** (`csv`, `os`, `random`, `re`, `logging`, `dataclasses`, `typing`, `datetime`, and `unittest` for tests)[cite: 1, 2, 7, 8]—no third-party `pip` packages are required for core execution.
* **Program Entry Point:** `cli.py` (`python3 cli.py`)[cite: 5].

---

## Input, Output & Log File Locations

All runtime data and log files are resolved relative to the current working directory under `data/`[cite: 1, 2, 4, 8]:

* **Destinations Input:** `data/destination.csv` (optional; if absent, `loader.py` falls back to the 15 default Spanish destinations from Madrid).
* **Offers Dataset:** `data/offers.csv` (automatically generated on first load by `loader.py` when missing, or generated via `generate_offers.py`)[cite: 7, 8].
* **Bookings Output:** `data/bookings.csv` (appended when a simulated group booking is confirmed)[cite: 4].
* **Travel Credits Store:** `data/credits.csv` (stores user credit balances; new users start with a default balance when the file is absent)[cite: 1].
* **Application Log:** `data/app_events.log` (records session events, filtering summaries, voucher redemptions, and bookings)[cite: 1, 2, 6].
* **Rejected Records Log:** `data/rejected_records.log` (records malformed or invalid CSV rows rejected during data loading).

---

## Running the Application

Run the CLI from the project root directory:

```bash
python3 cli.py