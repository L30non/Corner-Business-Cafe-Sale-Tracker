"""Flask Application for Corner Cafe Tracker."""

import threading
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from core import products, cart as cart_ops, sales, discounts, reports
from core.money import format_money, dollars_to_cents
import storage

app = Flask(__name__)
app.secret_key = "corner-cafe-secret-key-change-in-production"

# Load initial store state
store = storage.load_data()
store_lock = threading.Lock()

# Register custom Jinja filter for money
app.jinja_env.filters["money"] = format_money


@app.route("/")
def dashboard():
    """Dashboard route showing net revenue, sales count, low stock alerts."""
    with store_lock:
        report = reports.build_report(store)
    return render_template("dashboard.html", report=report)


@app.route("/products")
def products_page():
    """Product catalog management page."""
    with store_lock:
        catalog = store["catalog"]
    return render_template("products.html", catalog=catalog)


@app.post("/products/add")
def add_product_route():
    """Handle adding a new product to the catalog."""
    try:
        name = request.form.get("name", "").strip()
        price_str = request.form.get("price", "0")
        stock_str = request.form.get("stock", "0")
        category = request.form.get("category", "").strip() or "General"

        price_cents = dollars_to_cents(price_str)
        stock = int(stock_str)

        with store_lock:
            products.add_product(store, name, price_cents, stock, category)
            storage.save_data(store)

        flash(f"Product '{name}' added successfully.", "success")
    except ValueError as err:
        flash(str(err), "error")

    return redirect(url_for("products_page"))


@app.post("/products/<name>/stock")
def update_stock_route(name):
    """Handle updating product stock level."""
    try:
        stock_str = request.form.get("stock", "0")
        new_stock = int(stock_str)

        with store_lock:
            products.update_stock(store, name, new_stock)
            storage.save_data(store)

        flash(f"Stock for '{name}' updated to {new_stock}.", "success")
    except ValueError as err:
        flash(str(err), "error")

    return redirect(url_for("products_page"))


@app.post("/products/<name>/remove")
def remove_product_route(name):
    """Handle removing a product from the catalog."""
    try:
        with store_lock:
            products.remove_product(store, name)
            storage.save_data(store)

        flash(f"Product '{name}' removed from catalog.", "success")
    except ValueError as err:
        flash(str(err), "error")

    return redirect(url_for("products_page"))


@app.route("/sales/new")
def new_sale_page():
    """New sale/cart page with product picker and live totals."""
    cart = session.setdefault("cart", [])
    with store_lock:
        catalog = store["catalog"]
        cart_preview = cart_ops.preview_cart(store, cart)
    return render_template("new_sale.html", catalog=catalog, cart=cart, cart_preview=cart_preview)


@app.post("/cart/add")
def add_to_cart_route():
    """Add an item to the session cart."""
    cart = session.setdefault("cart", [])
    try:
        name = request.form.get("name", "").strip()
        qty = int(request.form.get("qty", "1"))

        with store_lock:
            cart_ops.add_to_cart(store, cart, name, qty)

        session.modified = True
        flash(f"Added {qty}x '{name}' to cart.", "success")
    except ValueError as err:
        flash(str(err), "error")

    return redirect(url_for("new_sale_page"))


@app.post("/cart/remove")
def remove_from_cart_route():
    """Remove an item from the cart."""
    cart = session.setdefault("cart", [])
    name = request.form.get("name", "").strip()
    cart_ops.remove_from_cart(cart, name)
    session.modified = True
    flash(f"Removed '{name}' from cart.", "success")
    return redirect(url_for("new_sale_page"))


@app.post("/cart/clear")
def clear_cart_route():
    """Clear all items from the cart."""
    session["cart"] = []
    session.modified = True
    flash("Cart cleared.", "success")
    return redirect(url_for("new_sale_page"))


@app.post("/checkout")
def checkout_route():
    """Complete checkout and record sale."""
    cart = session.setdefault("cart", [])
    try:
        with store_lock:
            sale = sales.checkout(store, cart)
            storage.save_data(store)

        session["cart"] = []
        session.modified = True
        flash(f"Sale #{sale['id']} completed successfully!", "success")
        return redirect(url_for("sale_detail_page", sale_id=sale["id"]))
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for("new_sale_page"))


@app.route("/sales")
def sales_history_page():
    """Sales history list (newest first)."""
    with store_lock:
        # Show sales in reverse chronological order (newest first)
        history = list(reversed(store["sales"]))
    return render_template("sales.html", sales=history)


@app.route("/sales/<int:sale_id>")
def sale_detail_page(sale_id):
    """Sale detail view with manual discount option."""
    with store_lock:
        sale = sales.find_sale(store, sale_id)

    if not sale:
        abort(404)

    return render_template("sale_detail.html", sale=sale)


@app.post("/sales/<int:sale_id>/discount")
def apply_discount_route(sale_id):
    """Apply manual discount override to a past sale."""
    try:
        percent = int(request.form.get("percent", "0"))
        with store_lock:
            sales.apply_manual_discount(store, sale_id, percent)
            storage.save_data(store)

        flash(f"Manual discount of {percent}% applied to Sale #{sale_id}.", "success")
    except ValueError as err:
        flash(str(err), "error")

    return redirect(url_for("sale_detail_page", sale_id=sale_id))


@app.route("/report")
def report_page():
    """Full revenue report page."""
    with store_lock:
        report = reports.build_report(store)
    return render_template("report.html", report=report)


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 error page."""
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
