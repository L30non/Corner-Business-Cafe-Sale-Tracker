"""Revenue reporting and analytics."""


def build_report(store):
    """Generate a comprehensive revenue report.

    Args:
        store: The store dictionary

    Returns:
        Dictionary with all report metrics
    """
    sales = store["sales"]
    catalog = store["catalog"]

    if not sales:
        return {
            "sale_count": 0,
            "gross": 0,
            "discounts": 0,
            "net": 0,
            "average_sale": None,
            "units_by_item": {},
            "best_seller": None,
            "bottom_seller": None,
            "revenue_by_category": {},
            "low_stock": [(name, prod["stock"])
                         for name, prod in catalog.items()
                         if prod["stock"] < 5]
        }

    # Calculate totals
    gross = sum(sale["subtotal"] for sale in sales)
    total_auto = sum(sale["auto_discount"] for sale in sales)
    total_manual = sum(sale["manual_discount"] for sale in sales)
    discounts = total_auto + total_manual
    net = sum(sale["total"] for sale in sales)
    average_sale = net // len(sales)

    # Count units by item
    units_by_item = {}
    for sale in sales:
        for line in sale["lines"]:
            item = line["item"]
            qty = line["qty"]
            units_by_item[item] = units_by_item.get(item, 0) + qty

    # Find best and bottom sellers
    best_seller = None
    bottom_seller = None
    if units_by_item:
        best_seller = max(units_by_item, key=units_by_item.get)
        bottom_seller = min(units_by_item, key=units_by_item.get)

    # Revenue by category
    revenue_by_category = {}
    for sale in sales:
        for line in sale["lines"]:
            category = line["category"]
            revenue_by_category[category] = \
                revenue_by_category.get(category, 0) + line["line_total"]

    # Low stock items
    low_stock = [(name, prod["stock"])
                 for name, prod in catalog.items()
                 if prod["stock"] < 5]

    return {
        "sale_count": len(sales),
        "gross": gross,
        "discounts": discounts,
        "net": net,
        "average_sale": average_sale,
        "units_by_item": units_by_item,
        "best_seller": best_seller,
        "bottom_seller": bottom_seller,
        "revenue_by_category": revenue_by_category,
        "low_stock": low_stock
    }
