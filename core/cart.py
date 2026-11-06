"""Shopping cart operations."""


def add_to_cart(store, cart, name, qty):
    """Add an item to the cart with stock validation.

    Args:
        store: The store dictionary
        cart: The cart list (mutated in place)
        name: Product name
        qty: Quantity to add (must be > 0)

    Raises:
        ValueError: If product doesn't exist, qty invalid, or exceeds stock
    """
    if name not in store["catalog"]:
        raise ValueError(f"Product '{name}' not found")

    if qty <= 0:
        raise ValueError("Quantity must be greater than zero")

    # Check current stock
    available_stock = store["catalog"][name]["stock"]

    # Count how many are already in cart
    current_in_cart = 0
    for line in cart:
        if line["item"] == name:
            current_in_cart = line["qty"]
            break

    # Validate total doesn't exceed stock
    total_requested = current_in_cart + qty
    if total_requested > available_stock:
        raise ValueError(
            f"Not enough stock for '{name}'. Available: {available_stock}, "
            f"already in cart: {current_in_cart}"
        )

    # Add to cart (merge if already exists)
    found = False
    for line in cart:
        if line["item"] == name:
            line["qty"] += qty
            found = True
            break

    if not found:
        cart.append({"item": name, "qty": qty})


def remove_from_cart(cart, name):
    """Remove an item from the cart.

    Args:
        cart: The cart list (mutated in place)
        name: Product name to remove
    """
    # Remove the item (no-op if not present)
    cart[:] = [line for line in cart if line["item"] != name]


def preview_cart(store, cart):
    """Calculate cart totals for display without checking out.

    Args:
        store: The store dictionary
        cart: The cart list

    Returns:
        Dict with subtotal, total_qty, discount_percent, auto_discount, estimated_total
    """
    from core.discounts import get_discount_percent

    if not cart:
        return {
            "subtotal": 0,
            "total_qty": 0,
            "discount_percent": 0,
            "auto_discount": 0,
            "estimated_total": 0
        }

    subtotal = 0
    total_qty = 0

    for line in cart:
        item_name = line["item"]
        qty = line["qty"]

        # Get current price from catalog
        if item_name in store["catalog"]:
            price = store["catalog"][item_name]["price"]
            subtotal += price * qty
            total_qty += qty

    discount_percent = get_discount_percent(store, total_qty)
    auto_discount = subtotal * discount_percent // 100
    estimated_total = subtotal - auto_discount

    return {
        "subtotal": subtotal,
        "total_qty": total_qty,
        "discount_percent": discount_percent,
        "auto_discount": auto_discount,
        "estimated_total": estimated_total
    }
