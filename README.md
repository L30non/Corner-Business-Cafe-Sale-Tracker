# Corner Cafe Tracker

A small Flask web app for running a corner cafe: manage the product catalog, ring up sales with a cart, apply quantity discounts, and review revenue reports. Data is stored in a single JSON file, so there is no database to set up.

Final project for *Survey of Computer Science* (Python).

## Features

- **Dashboard** – net revenue, sales count, and low-stock alerts at a glance
- **Product catalog** – add products, update stock levels, remove products
- **New sale / cart** – session-based cart with live totals and checkout
- **Automatic discounts** – quantity tiers (default: 5+ items = 5%, 10+ items = 10%)
- **Manual discounts** – apply a percentage discount to a past sale
- **Sales history** – newest first, with a detail page per sale
- **Revenue report** – gross, discounts, net, average sale, best/bottom seller, revenue by category
- **Money safety** – all amounts are stored as integer cents and formatted only for display

## Requirements

- Python 3.9+
- Flask 3.0.0 and Werkzeug 3.0.1 (see `requirements.txt`)

## Getting Started

```bash
# 1. (Optional) create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Run the app
python3 app.py
```

Open <http://localhost:5000> in your browser.

> Run the app from the project folder: `data.json` is read and written relative to the current working directory.

## Running the Tests

```bash
python3 -m unittest test_app.py
```

**Warning:** the tests overwrite `data.json` and delete it on teardown. Back it up first if it holds data you want to keep.

## Project Structure

```
.
├── app.py              # Flask routes and app setup
├── storage.py          # Load/save the store to data.json
├── core/               # Business logic (no Flask dependencies)
│   ├── products.py     #   catalog add / update stock / remove
│   ├── cart.py         #   add / remove / preview cart
│   ├── sales.py        #   checkout, find sale, manual discounts
│   ├── discounts.py    #   quantity discount tiers
│   ├── reports.py      #   revenue report metrics
│   └── money.py        #   cents <-> dollars helpers
├── templates/          # Jinja2 pages (dashboard, products, new sale, sales, report, 404/500)
├── static/style.css    # Styling
├── test_app.py         # Automated tests
├── data.json           # Persistent store (created/updated at runtime)
└── ONLINE_SHOPPING_GUIDE.md   # Spec for a customer-facing shop that shares data.json
```

## Data Format

Everything lives in `data.json`:

```json
{
  "catalog": {
    "Matcha Latte": { "price": 300, "stock": 7, "category": "Drinks" }
  },
  "sales": [
    {
      "id": 1,
      "date": "2026-11-05 15:00",
      "lines": [
        { "item": "Matcha Latte", "category": "Drinks", "qty": 2, "unit_price": 300, "line_total": 600 }
      ],
      "subtotal": 600,
      "auto_discount": 0,
      "manual_discount": 0,
      "total": 600
    }
  ],
  "discount_tiers": [[10, 10], [5, 5]],
  "next_sale_id": 2
}
```

- Prices and totals are in **cents** (`300` = `$3.00`).
- `discount_tiers` are `[min_qty, percent]` pairs, highest quantity first.
- If `data.json` is missing or corrupt, the app starts with an empty store.

## Notes

- The Flask `secret_key` in `app.py` is a placeholder. Change it before any real deployment.
- The app runs with `debug=True` on `0.0.0.0:5000`, which is fine for local development but not for production.
