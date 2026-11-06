"""Data persistence layer - JSON file storage."""

import json
import os


def load_data():
    """Load store data from data.json.

    Returns:
        Store dictionary with default structure if file missing/corrupt
    """
    default_store = {
        "catalog": {},
        "sales": [],
        "discount_tiers": [(10, 10), (5, 5)],  # (min_qty, percent)
        "next_sale_id": 1
    }

    if not os.path.exists("data.json"):
        return default_store

    try:
        with open("data.json", "r") as f:
            store = json.load(f)

        # Ensure discount_tiers are tuples (JSON converts them to lists)
        if "discount_tiers" in store:
            store["discount_tiers"] = [tuple(tier) for tier in store["discount_tiers"]]

        # Ensure all required keys exist
        for key in default_store:
            if key not in store:
                store[key] = default_store[key]

        return store

    except (json.JSONDecodeError, IOError):
        # Corrupt or unreadable - return default
        return default_store


def save_data(store):
    """Save store data to data.json.

    Args:
        store: The store dictionary to persist
    """
    with open("data.json", "w") as f:
        json.dump(store, f, indent=2)
