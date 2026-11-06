"""Sales transaction handling."""

from datetime import datetime
from core.discounts import get_discount_percent


def checkout(store, cart):
    """Complete a sale, deduct stock, and record the transaction.

    Args:
        store: The store dictionary (mutated)
        cart: The cart list

    Returns:
        The completed sale dictionary

    Raises:
        ValueError: If cart is empty or stock insufficient
    """
    if not cart:
        raise ValueError("Cart is empty - add items before checking out")

    # Re-validate stock (could have changed since items were added)
    for line in cart:
        item_name = line["item"]
        qty = line["qty"]

        if item_name not in store["catalog"]:
            raise ValueError(f"Product '{item_name}' no longer exists")

        available = store["catalog"][item_name]["stock"]
        if qty > available:
            raise ValueError(
                f"Insufficient stock for '{item_name}'. "
                f"Need {qty}, have {available}"
            )

    # Build sale lines and calculate totals
    lines = []
    subtotal = 0
    total_qty = 0

    for cart_line in cart:
        item_name = cart_line["item"]
        qty = cart_line["qty"]
        product = store["catalog"][item_name]

        unit_price = product["price"]
        line_total = unit_price * qty

        lines.append({
            "item": item_name,
            "category": product["category"],
            "qty": qty,
            "unit_price": unit_price,
            "line_total": line_total
        })

        subtotal += line_total
        total_qty += qty

    # Calculate discount
    discount_percent = get_discount_percent(store, total_qty)
    auto_discount = subtotal * discount_percent // 100
    total = subtotal - auto_discount

    # Create sale record
    sale = {
        "id": store["next_sale_id"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "lines": lines,
        "subtotal": subtotal,
        "auto_discount": auto_discount,
        "manual_discount": 0,
        "total": total
    }

    # Deduct stock
    for cart_line in cart:
        item_name = cart_line["item"]
        qty = cart_line["qty"]
        store["catalog"][item_name]["stock"] -= qty

    # Record sale
    store["sales"].append(sale)
    store["next_sale_id"] += 1

    return sale


def find_sale(store, sale_id):
    """Find a sale by ID.

    Args:
        store: The store dictionary
        sale_id: The sale ID to find

    Returns:
        Sale dictionary or None if not found
    """
    for sale in store["sales"]:
        if sale["id"] == sale_id:
            return sale
    return None


def apply_manual_discount(store, sale_id, percent):
    """Apply a manual discount to a past sale.

    Args:
        store: The store dictionary (mutated)
        sale_id: The sale ID
        percent: Discount percentage (0-100)

    Returns:
        Updated sale dictionary

    Raises:
        ValueError: If sale not found or percent invalid
    """
    sale = find_sale(store, sale_id)
    if not sale:
        raise ValueError(f"Sale #{sale_id} not found")

    if percent < 0 or percent > 100:
        raise ValueError("Discount must be between 0 and 100")

    # Manual discount replaces auto discount
    manual_discount = sale["subtotal"] * percent // 100
    sale["manual_discount"] = manual_discount
    sale["total"] = sale["subtotal"] - manual_discount

    return sale
