import unittest

# --- Application Logic ---

class Product:
    """Represents a product with a name and price."""
    def __init__(self, name, price):
        if not isinstance(name, str) or not name:
            raise ValueError("Product name must be a non-empty string.")
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Product price must be a positive number.")
        self.name = name
        self.price = price

class ShoppingCart:
    """Manages items added to a shopping cart."""
    def __init__(self):
        self.items = {} # {product_name: (product_obj, quantity)}

    def add_item(self, product, quantity=1):
        if not isinstance(product, Product):
            raise TypeError("Item must be a Product instance.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        
        if product.name in self.items:
            current_product, current_quantity = self.items[product.name]
            self.items[product.name] = (product, current_quantity + quantity)
        else:
            self.items[product.name] = (product, quantity)

    def remove_item(self, product_name, quantity=1):
        if not isinstance(product_name, str) or not product_name:
            raise ValueError("Product name must be a non-empty string.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        if product_name not in self.items:
            raise ValueError(f"Product '{product_name}' not in cart.")
        
        current_product, current_quantity = self.items[product_name]
        if current_quantity <= quantity:
            del self.items[product_name]
        else:
            self.items[product_name] = (current_product, current_quantity - quantity)

    def get_total(self):
        total = 0
        for product, quantity in self.items.values():
            total += product.price * quantity
        return total

class OrderProcessor:
    """Processes a shopping cart into an order, applying discounts and simulating persistence."""
    def __init__(self, discount_rate=0.1):
        if not isinstance(discount_rate, (int, float)) or not (0 <= discount_rate < 1):
            raise ValueError("Discount rate must be between 0 and 1.")
        self.discount_rate = discount_rate
        self.processed_orders = [] # In-memory store for demonstration

    def process_order(self, cart):
        if not isinstance(cart, ShoppingCart):
            raise TypeError("Cart must be a ShoppingCart instance.")
        
        subtotal = cart.get_total()
        discount_amount = subtotal * self.discount_rate
        final_total = subtotal - discount_amount
        
        order_details = {
            "items": {p.name: q for p, q in cart.items.values()},
            "subtotal": subtotal,
            "discount_applied": discount_amount,
            "final_total": final_total
        }
        self._save_order(order_details) # Simulate persistence
        return order_details

    def _save_order(self, order_details):
        # In a real application, this would interact with a database or external service.
        # For this example, we just store it in memory.
        self.processed_orders.append(order_details)
        print(f"  [Simulated DB] Order saved: {order_details['final_total']:.2f}")

# --- Test Pyramid Layers ---

class TestUnit(unittest.TestCase):
    """Unit tests: Fast, isolated tests for individual functions/components."""
    def setUp(self):
        self.product1 = Product("Laptop", 1000)
        self.product2 = Product("Mouse", 25)
        self.cart = ShoppingCart()
        self.processor = OrderProcessor(discount_rate=0.1)

    def test_add_item_to_cart_isolated(self):
        # Unit test: Test a single method of ShoppingCart in isolation
        self.cart.add_item(self.product1, 2)
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.items["Laptop"][1], 2)

    def test_remove_item_from_cart_isolated(self):
        self.cart.add_item(self.product1, 3)
        self.cart.remove_item("Laptop", 1)
        self.assertEqual(self.cart.items["Laptop"][1], 2)

    def test_processor_discount_calculation_isolated(self):
        # Unit test: Test a specific calculation logic of OrderProcessor
        # Use a mock cart to isolate OrderProcessor's logic
        mock_cart = type('MockCart', (object,), {'get_total': lambda self: 100})() 
        order_details = self.processor.process_order(mock_cart)
        self.assertEqual(order_details["subtotal"], 100)
        self.assertEqual(order_details["discount_applied"], 10) # 10% of 100
        self.assertEqual(order_details["final_total"], 90)

class TestIntegration(unittest.TestCase):
    """Integration tests: Test interactions between different components."""
    def setUp(self):
        self.product1 = Product("Keyboard", 75)
        self.product2 = Product("Monitor", 300)
        self.cart = ShoppingCart()
        self.processor = OrderProcessor(discount_rate=0.05) # 5% discount

    def test_cart_product_interaction(self):
        # Integration test: Test ShoppingCart's interaction with Product objects
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 1)
        self.assertEqual(self.cart.get_total(), (75 * 2) + (300 * 1)) # 150 + 300 = 450

    def test_processor_cart_interaction(self):
        # Integration test: Test OrderProcessor's interaction with ShoppingCart
        self.cart.add_item(self.product1, 2) # 150
        self.cart.add_item(self.product2, 1) # 300
        # Cart total is 450
        
        order_details = self.processor.process_order(self.cart)
        self.assertEqual(order_details["subtotal"], 450)
        self.assertAlmostEqual(order_details["discount_applied"], 450 * 0.05) # 22.5
        self.assertAlmostEqual(order_details["final_total"], 450 - (450 * 0.05)) # 427.5
        self.assertIn(order_details, self.processor.processed_orders) # Verify simulated persistence

class TestE2E(unittest.TestCase):
    """End-to-End test: Simulate a complete user workflow from start to finish."""
    def setUp(self):
        self.processor = OrderProcessor(discount_rate=0.15) # High-level E2E discount

    def test_full_order_workflow(self):
        # End-to-End test: Simulate a complete user flow from product creation to order processing
        print("\n--- Running E2E Test: Full Order Workflow ---")
        
        # 1. Create products (simulating product catalog)
        product_a = Product("Smartphone", 800)
        product_b = Product("Headphones", 150)
        
        # 2. User adds items to cart
        cart = ShoppingCart()
        cart.add_item(product_a, 1)
        cart.add_item(product_b, 2) # Two headphones
        
        # 3. Verify cart state (intermediate check)
        self.assertEqual(cart.get_total(), 800 + (150 * 2)) # 800 + 300 = 1100
        print(f"  Cart total before processing: {cart.get_total():.2f}")

        # 4. Process the order
        order_details = self.processor.process_order(cart)
        
        # 5. Verify final order details (simulating order confirmation/database check)
        expected_subtotal = 1100
        expected_discount = expected_subtotal * 0.15
        expected_final_total = expected_subtotal - expected_discount
        
        self.assertEqual(order_details["subtotal"], expected_subtotal)
        self.assertAlmostEqual(order_details["discount_applied"], expected_discount)
        self.assertAlmostEqual(order_details["final_total"], expected_final_total)
        self.assertIn(order_details, self.processor.processed_orders)
        print(f"  Order processed successfully. Final total: {order_details['final_total']:.2f}")
        print("--- E2E Test Finished ---")

# --- Main Execution --- 

if __name__ == "__main__":
    print("Running Test Pyramid Example:")
    print("----------------------------")
    print("1. Unit Tests (Fast, Isolated, Bottom of Pyramid)")
    unittest.main(argv=['first-arg-is-ignored'], exit=False, defaultTest='TestUnit')
    print("\n2. Integration Tests (Component Interactions, Middle of Pyramid)")
    unittest.main(argv=['first-arg-is-ignored'], exit=False, defaultTest='TestIntegration')
    print("\n3. End-to-End Test (Full Workflow, Top of Pyramid)")
    unittest.main(argv=['first-arg-is-ignored'], exit=False, defaultTest='TestE2E')
    print("\n----------------------------")
    print("Test Pyramid demonstration complete.")