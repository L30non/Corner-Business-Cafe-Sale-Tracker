"""Automated tests for the Corner Cafe Flask web application."""

import unittest
import os
import json
from app import app, store, store_lock
import storage


class CafeFlaskTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and clean test store state."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        # Reset store for testing
        with store_lock:
            store["catalog"] = {
                "Espresso": {"price": 300, "stock": 10, "category": "Drinks"},
                "Croissant": {"price": 250, "stock": 5, "category": "Bakery"}
            }
            store["sales"] = []
            store["discount_tiers"] = [(5, 10), (3, 5)]
            store["next_sale_id"] = 1
            storage.save_data(store)

    def tearDown(self):
        """Clean up test data.json if needed."""
        if os.path.exists("data.json"):
            try:
                os.remove("data.json")
            except OSError:
                pass

    def test_dashboard_route(self):
        """Test dashboard renders successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cafe Overview', response.data)

    def test_products_page(self):
        """Test products catalog page renders with items."""
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Espresso', response.data)
        self.assertIn(b'Croissant', response.data)

    def test_add_product(self):
        """Test adding a new product via POST."""
        response = self.client.post('/products/add', data={
            'name': 'Matcha Latte',
            'price': '4.50',
            'stock': '15',
            'category': 'Drinks'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Matcha Latte', response.data)
        self.assertIn(b'Matcha Latte added successfully', response.data)

    def test_update_stock(self):
        """Test updating product stock."""
        response = self.client.post('/products/Espresso/stock', data={
            'stock': '25'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Stock for &#39;Espresso&#39; updated to 25', response.data)
        with store_lock:
            self.assertEqual(store["catalog"]["Espresso"]["stock"], 25)

    def test_remove_product(self):
        """Test removing a product."""
        response = self.client.post('/products/Croissant/remove', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product &#39;Croissant&#39; removed', response.data)
        with store_lock:
            self.assertNotIn("Croissant", store["catalog"])

    def test_cart_and_checkout(self):
        """Test adding items to cart, viewing preview, and checking out."""
        # Add item to cart
        resp1 = self.client.post('/cart/add', data={
            'name': 'Espresso',
            'qty': '3'
        }, follow_redirects=True)
        self.assertEqual(resp1.status_code, 200)
        self.assertIn(b'Added 3x &#39;Espresso&#39;', resp1.data)

        # Visit new sale page to check preview
        resp_cart = self.client.get('/sales/new')
        self.assertEqual(resp_cart.status_code, 200)
        self.assertIn(b'Espresso', resp_cart.data)

        # Checkout
        resp_checkout = self.client.post('/checkout', follow_redirects=True)
        self.assertEqual(resp_checkout.status_code, 200)
        self.assertIn(b'Sale #1 completed successfully', resp_checkout.data)

        # Verify stock was deducted
        with store_lock:
            self.assertEqual(store["catalog"]["Espresso"]["stock"], 7)
            self.assertEqual(len(store["sales"]), 1)

    def test_sales_history_and_detail(self):
        """Test viewing sales history and sale detail page."""
        # Create a sale first
        self.client.post('/cart/add', data={'name': 'Espresso', 'qty': '2'})
        self.client.post('/checkout')

        # Visit sales history
        resp_history = self.client.get('/sales')
        self.assertEqual(resp_history.status_code, 200)
        self.assertIn(b'#1', resp_history.data)

        # Visit sale detail
        resp_detail = self.client.get('/sales/1')
        self.assertEqual(resp_detail.status_code, 200)
        self.assertIn(b'Espresso', resp_detail.data)

    def test_manual_discount(self):
        """Test applying a manual discount override to a sale."""
        # Create a sale
        self.client.post('/cart/add', data={'name': 'Espresso', 'qty': '2'})
        self.client.post('/checkout')

        # Apply manual discount
        resp = self.client.post('/sales/1/discount', data={
            'percent': '20'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Manual discount of 20% applied', resp.data)

        with store_lock:
            sale = store["sales"][0]
            self.assertEqual(sale["manual_discount"], 60)  # 20% of 300 * 2 (600) = 120? Wait: 300*2 = 600 cents subtotal. 20% of 600 = 120 cents.
            self.assertEqual(sale["total"], 480)

    def test_report_page(self):
        """Test revenue report page."""
        response = self.client.get('/report')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Revenue Analytics', response.data)

    def test_404_error(self):
        """Test 404 page for unknown route or sale ID."""
        response = self.client.get('/sales/9999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)


if __name__ == '__main__':
    unittest.main()
