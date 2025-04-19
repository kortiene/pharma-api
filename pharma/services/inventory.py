import random
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from pymongo.collection import Collection

from pharma.services.agent import InventoryAgent
from pharma.models import Product, StockItem, StockMovement, StockThreshold
from pharma.utils import to_bson_safe_dict


class InventorySimulator(InventoryAgent):
    """Simulator for generating test data covering all StockAggregations scenarios."""

    def reset_database(self):
        """Clear all collections to start fresh."""
        self.db.products.delete_many({})
        self.db.movements.delete_many({})
        self.db.stocks.delete_many({})
        self.db.stock_thresholds.delete_many({})

    def update_stock(self, product_id: str, movement: StockMovement):
        """Update stock quantity based on movement type."""
        stock = self.db.stocks.find_one({"product_id": product_id})
        quantity = stock["quantity"] if stock else 0

        if movement.movement_type in ["ENTREE", "RETOUR"]:
            quantity += movement.quantity
        elif movement.movement_type in ["SORTIE", "RUPTURE"]:
            quantity -= movement.quantity
        quantity = max(quantity, 0)

        self.db.stocks.update_one(
            {"product_id": product_id},
            {"$set": {"quantity": quantity, "last_update": datetime.utcnow()}},
            upsert=True,
        )

    def create_base_products(self, count: int = 10) -> List[str]:
        """Create base products with random attributes."""
        product_ids = []
        categories = [
            "Antibiotique", "Antalgique", "Antipaludéen",
            "Antifongique", "Antiviral", "Antihypertenseur"
        ]

        for i in range(1, count + 1):
            p = Product(
                id=f"P00{i}",
                name=f"Produit-{i}",
                category=random.choice(categories),
                batch_number=f"BATCH00{i}",
                expiration_date=date.today() + timedelta(days=random.randint(60, 180)),
                unit_price=round(random.uniform(500, 5000), 2),
            )
            self.db.products.insert_one(to_bson_safe_dict(p))
            product_ids.append(p.id)
            
            # Initialize stock
            stock = StockItem(
                product_id=p.id,
                quantity=random.randint(10, 50),
                last_update=datetime.utcnow()
            )
            self.db.stocks.insert_one(to_bson_safe_dict(stock))

            # Set stock thresholds
            threshold = StockThreshold(
                product_id=p.id,
                minimum_stock=random.randint(5, 15),
                critical_stock=random.randint(2, 5)
            )
            self.db.stock_thresholds.insert_one(to_bson_safe_dict(threshold))

        return product_ids

    def create_expiring_products(self, count: int = 3) -> List[str]:
        """Create products that will expire soon for testing expiration scenarios."""
        product_ids = []
        for i in range(1, count + 1):
            p = Product(
                id=f"EXP{i}",
                name=f"Expiring-{i}",
                category="Test",
                batch_number=f"BATCH-EXP{i}",
                expiration_date=date.today() + timedelta(days=random.randint(1, 30)),
                unit_price=1000
            )
            self.db.products.insert_one(to_bson_safe_dict(p))
            product_ids.append(p.id)

            stock = StockItem(
                product_id=p.id,
                quantity=random.randint(1, 5),
                last_update=datetime.utcnow()
            )
            self.db.stocks.insert_one(to_bson_safe_dict(stock))

            threshold = StockThreshold(
                product_id=p.id,
                minimum_stock=5,
                critical_stock=2
            )
            self.db.stock_thresholds.insert_one(to_bson_safe_dict(threshold))

        return product_ids

    def create_critical_stock_products(self, count: int = 3) -> List[str]:
        """Create products with critical stock levels."""
        product_ids = []
        for i in range(1, count + 1):
            p = Product(
                id=f"CRIT{i}",
                name=f"Critical-{i}",
                category="Test",
                batch_number=f"BATCH-CRIT{i}",
                expiration_date=date.today() + timedelta(days=180),
                unit_price=1000
            )
            self.db.products.insert_one(to_bson_safe_dict(p))
            product_ids.append(p.id)

            stock = StockItem(
                product_id=p.id,
                quantity=random.randint(1, 3),  # Low quantity
                last_update=datetime.utcnow()
            )
            self.db.stocks.insert_one(to_bson_safe_dict(stock))

            threshold = StockThreshold(
                product_id=p.id,
                minimum_stock=10,
                critical_stock=5
            )
            self.db.stock_thresholds.insert_one(to_bson_safe_dict(threshold))

        return product_ids

    def create_high_consumption_products(self, count: int = 3) -> List[str]:
        """Create products with high consumption patterns."""
        product_ids = []
        for i in range(1, count + 1):
            p = Product(
                id=f"HIGH{i}",
                name=f"High-Consumption-{i}",
                category="Test",
                batch_number=f"BATCH-HIGH{i}",
                expiration_date=date.today() + timedelta(days=180),
                unit_price=1000
            )
            self.db.products.insert_one(to_bson_safe_dict(p))
            product_ids.append(p.id)

            stock = StockItem(
                product_id=p.id,
                quantity=random.randint(20, 30),
                last_update=datetime.utcnow()
            )
            self.db.stocks.insert_one(to_bson_safe_dict(stock))

            threshold = StockThreshold(
                product_id=p.id,
                minimum_stock=15,
                critical_stock=10
            )
            self.db.stock_thresholds.insert_one(to_bson_safe_dict(threshold))

        return product_ids

    def generate_movements(self, product_ids: List[str], months: int = 6):
        """Generate movement history for products."""
        start_date = date.today() - timedelta(days=months * 30)
        
        for product_id in product_ids:
            for month in range(months):
                ref_date = start_date + timedelta(days=month * 30)
                
                # Generate regular movements
                movements = [
                    StockMovement(
                        movement_type=random.choice(["ENTREE", "SORTIE"]),
                        product_id=product_id,
                        quantity=random.randint(1, 10),
                        date=datetime.combine(
                            ref_date + timedelta(days=random.randint(0, 29)),
                            datetime.min.time(),
                        ),
                        reason="simulation",
                    )
                    for _ in range(5)
                ]
                
                # Add occasional stockouts for high consumption products
                if product_id.startswith("HIGH"):
                    movements.append(
                        StockMovement(
                            movement_type="RUPTURE",
                            product_id=product_id,
                            quantity=random.randint(1, 5),
                            date=datetime.combine(
                                ref_date + timedelta(days=random.randint(0, 29)),
                                datetime.min.time(),
                            ),
                            reason="simulation_stockout",
                        )
                    )

                for m in movements:
                    self.db.movements.insert_one(to_bson_safe_dict(m))
                    self.update_stock(product_id, m)

    def run(self, months: int = 6):
        """Run the complete simulation."""
        self.reset_database()
        
        # Create different types of products
        base_products = self.create_base_products()
        expiring_products = self.create_expiring_products()
        critical_products = self.create_critical_stock_products()
        high_consumption_products = self.create_high_consumption_products()
        
        # Combine all product IDs
        all_products = (
            base_products + 
            expiring_products + 
            critical_products + 
            high_consumption_products
        )
        
        # Generate movement history
        self.generate_movements(all_products, months)

    def init_inventory():
        """Initialize the inventory simulator."""
        simulator = InventorySimulator()
        simulator.run()
        return simulator