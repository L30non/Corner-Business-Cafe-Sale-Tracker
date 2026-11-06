"""Discount tier calculation."""


def get_discount_percent(store, total_qty):
    """Get the discount percentage for a given quantity.

    Args:
        store: The store dictionary
        total_qty: Total quantity of items

    Returns:
        Discount percentage (integer) or 0 if no tier matches
    """
    # Tiers are stored as (min_qty, percent), sorted highest min_qty first
    for min_qty, percent in store["discount_tiers"]:
        if total_qty >= min_qty:
            return percent

    return 0
