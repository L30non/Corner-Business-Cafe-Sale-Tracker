"""Product catalog management."""


def add_product(store, name, price_cents, stock, category):
    """Add a new product to the catalog.

    Args:
        store: The store dictionary
        name: Product name (must be non-empty and unique)
        price_cents: Price in cents (must be > 0)
        stock: Initial stock quantity (must be >= 0)
        category: Product category (e.g., "Drinks", "Bakery")

    Raises:
        ValueError: If validation fails
    """
    if not name or not name.strip():
        raise ValueError("Product name cannot be empty")

    if name in store["catalog"]:
        raise ValueError(f"Product '{name}' already exists")

    if price_cents <= 0:
        raise ValueError("Price must be greater than zero")

    if stock < 0:
        raise ValueError("Stock cannot be negative")

    store["catalog"][name] = {
        "price": price_cents,
        "stock": stock,
        "category": category
    }


def update_stock(store, name, new_stock):
    """Update the stock quantity for a product.

    Args:
        store: The store dictionary
        name: Product name
        new_stock: New stock quantity (must be >= 0)

    Raises:
        ValueError: If product doesn't exist or stock is negative
    """
    if name not in store["catalog"]:
        raise ValueError(f"Product '{name}' not found")

    if new_stock < 0:
        raise ValueError("Stock cannot be negative")

    store["catalog"][name]["stock"] = new_stock


def remove_product(store, name):
    """Remove a product from the catalog.

    Args:
        store: The store dictionary
        name: Product name

    Raises:
        ValueError: If product doesn't exist
    """
    if name not in store["catalog"]:
        raise ValueError(f"Product '{name}' not found")

    del store["catalog"][name]
