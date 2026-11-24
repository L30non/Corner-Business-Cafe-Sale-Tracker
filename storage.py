"""Data persistence layer - SQLite storage (open cafe.db in DB Browser for SQLite)."""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cafe.db")

DEFAULT_TIERS = [(10, 10), (5, 5)]  # (min_qty, percent)

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    name     TEXT PRIMARY KEY,
    price    INTEGER NOT NULL,           -- cents
    stock    INTEGER NOT NULL,
    category TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sales (
    id              INTEGER PRIMARY KEY,
    date            TEXT NOT NULL,       -- 'YYYY-MM-DD HH:MM'
    subtotal        INTEGER NOT NULL,    -- cents
    auto_discount   INTEGER NOT NULL,    -- cents
    manual_discount INTEGER NOT NULL,    -- cents
    total           INTEGER NOT NULL     -- cents
);
CREATE TABLE IF NOT EXISTS sale_lines (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id    INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    item       TEXT NOT NULL,
    category   TEXT NOT NULL,
    qty        INTEGER NOT NULL,
    unit_price INTEGER NOT NULL,         -- cents
    line_total INTEGER NOT NULL          -- cents
);
CREATE TABLE IF NOT EXISTS discount_tiers (
    min_qty INTEGER PRIMARY KEY,
    percent INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);
"""


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def load_data():
    """Load store data from cafe.db.

    Returns:
        Store dictionary (catalog, sales, discount_tiers, next_sale_id).
        Defaults are returned for anything not yet stored.
    """
    store = {
        "catalog": {},
        "sales": [],
        "discount_tiers": list(DEFAULT_TIERS),
        "next_sale_id": 1,
    }

    try:
        conn = _connect()
    except sqlite3.Error:
        return store

    try:
        for name, price, stock, category in conn.execute(
            "SELECT name, price, stock, category FROM products ORDER BY rowid"
        ):
            store["catalog"][name] = {"price": price, "stock": stock, "category": category}

        lines_by_sale = {}
        for sale_id, item, category, qty, unit_price, line_total in conn.execute(
            "SELECT sale_id, item, category, qty, unit_price, line_total "
            "FROM sale_lines ORDER BY id"
        ):
            lines_by_sale.setdefault(sale_id, []).append({
                "item": item, "category": category, "qty": qty,
                "unit_price": unit_price, "line_total": line_total,
            })

        for sid, date, subtotal, auto, manual, total in conn.execute(
            "SELECT id, date, subtotal, auto_discount, manual_discount, total "
            "FROM sales ORDER BY id"
        ):
            store["sales"].append({
                "id": sid, "date": date, "lines": lines_by_sale.get(sid, []),
                "subtotal": subtotal, "auto_discount": auto,
                "manual_discount": manual, "total": total,
            })

        tiers = conn.execute(
            "SELECT min_qty, percent FROM discount_tiers ORDER BY min_qty DESC"
        ).fetchall()
        if tiers:
            store["discount_tiers"] = [tuple(t) for t in tiers]

        row = conn.execute("SELECT value FROM meta WHERE key = 'next_sale_id'").fetchone()
        if row:
            store["next_sale_id"] = row[0]
        elif store["sales"]:
            store["next_sale_id"] = max(s["id"] for s in store["sales"]) + 1
    finally:
        conn.close()

    return store


def save_data(store):
    """Persist the store dictionary to cafe.db (replaces previous contents atomically).

    Args:
        store: The store dictionary to persist
    """
    conn = _connect()
    try:
        with conn:  # single transaction: commit on success, roll back on error
            for table in ("sale_lines", "sales", "products", "discount_tiers", "meta"):
                conn.execute(f"DELETE FROM {table}")

            conn.executemany(
                "INSERT INTO products (name, price, stock, category) VALUES (?, ?, ?, ?)",
                [(n, p["price"], p["stock"], p["category"]) for n, p in store["catalog"].items()],
            )
            for sale in store["sales"]:
                conn.execute(
                    "INSERT INTO sales (id, date, subtotal, auto_discount, manual_discount, total) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (sale["id"], sale["date"], sale["subtotal"], sale["auto_discount"],
                     sale["manual_discount"], sale["total"]),
                )
                conn.executemany(
                    "INSERT INTO sale_lines (sale_id, item, category, qty, unit_price, line_total) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    [(sale["id"], l["item"], l["category"], l["qty"], l["unit_price"], l["line_total"])
                     for l in sale["lines"]],
                )
            conn.executemany(
                "INSERT INTO discount_tiers (min_qty, percent) VALUES (?, ?)",
                [tuple(t) for t in store["discount_tiers"]],
            )
            conn.execute(
                "INSERT INTO meta (key, value) VALUES ('next_sale_id', ?)",
                (store["next_sale_id"],),
            )
    finally:
        conn.close()
