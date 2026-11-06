"""Money handling utilities - always use integer cents internally."""


def format_money(cents):
    """Convert cents to dollar string format.

    Args:
        cents: Integer amount in cents

    Returns:
        Formatted string like "$9.80"
    """
    dollars = cents / 100
    return f"${dollars:.2f}"


def dollars_to_cents(text):
    """Convert dollar string to integer cents.

    Args:
        text: String representation of dollars (e.g., "3.50")

    Returns:
        Integer cents (e.g., 350)

    Raises:
        ValueError: If text is not numeric or is negative
    """
    try:
        amount = float(text)
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        return int(amount * 100)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid amount: '{text}' must be a valid number")
