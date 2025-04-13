import random
from datetime import date, datetime, timedelta

from pharma.services.agent import InventoryAgent
from pharma.models import Product, StockItem, StockMovement
from pharma.utils import to_bson_safe_dict


class InventorySimulator(InventoryAgent):

    def reset_database(self):
        self.db.products.delete_many({})
        self.db.movements.delete_many({})
        self.db.stocks.delete_many({})

    def update_stock(self, product_id: str, movement: StockMovement):
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

    def run(self, months: int = 6, products_count: int = 10):
        self.reset_database()
        start_date = date.today() - timedelta(days=months * 30)
        product_ids = []

        for i in range(1, products_count + 1):
            p = Product(
                id=f"P00{i}",
                name=f"Produit-{i}",
                category=random.choice(
                    [
                        "Antibiotique",
                        "Antalgique",
                        "Antipaludéen",
                        "Antifongique",
                        "Antiviral",
                        "Antihypertenseur",
                    ]
                ),
                batch_number=f"BATCH00{i}",
                expiration_date=date.today() + timedelta(days=random.randint(60, 180)),
                unit_price=round(random.uniform(500, 5000), 2),
            )
            self.db.products.insert_one(to_bson_safe_dict(p))
            product_ids.append(p.id)
            # Initialiser le stock à 0
            stock = StockItem(
                product_id=p.id, quantity=0, last_update=datetime.utcnow()
            )
            self.db.stocks.insert_one(to_bson_safe_dict(stock))

        for product_id in product_ids:
            for month in range(months):
                ref_date = start_date + timedelta(days=month * 30)
                movements = [
                    StockMovement(
                        movement_type=random.choice(["ENTREE", "SORTIE", "RUPTURE"]),
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
                for m in movements:
                    self.db.movements.insert_one(to_bson_safe_dict(m))
                    self.update_stock(product_id, m)

def init_inventory():
    inventory = InventorySimulator()
    inventory.reset_database()
    inventory.run(months=6, products_count=100)
    print("Simulation enrichie terminée avec succès.")