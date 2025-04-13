from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

from pymongo import MongoClient

from pharma.models import Alert, ForecastResult, KPIReport, PurchaseProposal
from pharma.settings import SETTINGS

# --- AGENT IA ---


class InventoryAgent:
    def __init__(self):
        self.client = MongoClient(SETTINGS.mongodb_url)
        self.db = self.client[SETTINGS.mongodb_name]


# --- SMART AGENT ---


class SmartInventoryAgent(InventoryAgent):

    def forecast_consumption(self, months: int = 3) -> List[ForecastResult]:
        cutoff_date = datetime.utcnow() - timedelta(days=30 * months)
        movements = list(
            self.db.movements.find(
                {"movement_type": "SORTIE", "date": {"$gte": cutoff_date}}
            )
        )
        consumption = defaultdict(int)

        for m in movements:
            consumption[m["product_id"]] += m["quantity"]

        forecasts = []
        for product_id, total in consumption.items():
            average = total / months
            stock = self.db.stocks.find_one({"product_id": product_id}) or {
                "quantity": 0
            }
            suggested = max(0, int(average * 2 - stock["quantity"]))
            forecasts.append(
                ForecastResult(
                    product_id=product_id,
                    average_consumption=average,
                    suggested_quantity=suggested,
                )
            )
        return forecasts

    def detect_critical_stocks(self, critical_level: int = 10) -> List[Alert]:
        alerts = []
        for s in self.db.stocks.find():
            if s["quantity"] <= critical_level:
                alerts.append(
                    Alert(
                        product_id=s["product_id"],
                        alert_type="SEUIL_CRITIQUE",
                        message=f"Stock critique pour {s['product_id']} ({s['quantity']} unités)",
                        date=datetime.utcnow(),
                    )
                )
        return alerts

    def detect_expiring_products(self, days_limit: int = 30) -> List[Alert]:
        alerts = []
        for p in self.db.products.find():
            if (
                p["expiration_date"].date() - datetime.utcnow().date()
            ).days <= days_limit:
                alerts.append(
                    Alert(
                        product_id=p["id"],
                        alert_type="PEREMPTION",
                        message=f"Produit {p['id']} proche de péremption ({p['expiration_date']})",
                        date=datetime.utcnow(),
                    )
                )
        return alerts

    def simulate_inventory_audit(self) -> List[Alert]:
        alerts = []
        for product in self.db.products.find():
            stock = self.db.stocks.find_one({"product_id": product["id"]}) or {
                "quantity": 0
            }
            theoretical_qty = sum(
                (
                    m["quantity"]
                    if m["movement_type"] in ["ENTREE", "RETOUR"]
                    else -m["quantity"]
                )
                for m in self.db.movements.find({"product_id": product["id"]})
            )
            if abs(stock["quantity"] - theoretical_qty) > 5:
                alerts.append(
                    Alert(
                        product_id=product["id"],
                        alert_type="INVENTAIRE_ECART",
                        message=f"Écart détecté : stock={stock['quantity']}, attendu={theoretical_qty}",
                        date=datetime.utcnow(),
                    )
                )
        return alerts

    def generate_kpi_report(self) -> KPIReport:
        ruptures = list(self.db.movements.find({"movement_type": "RUPTURE"}))
        sorties = list(self.db.movements.find({"movement_type": "SORTIE"}))
        counter = defaultdict(int)
        for s in sorties:
            counter[s["product_id"]] += s["quantity"]
        top_products = sorted(counter, key=counter.get, reverse=True)[:5]
        return KPIReport(
            total_ruptures=len(ruptures),
            total_exits=sum(counter.values()),
            top_products=top_products,
        )

    def suggest_purchase_orders(self) -> List[PurchaseProposal]:
        suggestions = []
        forecasts = self.forecast_consumption()
        for forecast in forecasts:
            if forecast.suggested_quantity > 0:
                suggestions.append(
                    PurchaseProposal(
                        product_id=forecast.product_id,
                        suggested_quantity=forecast.suggested_quantity,
                        based_on="Prévision",
                        justification="Basé sur la prévision de consommation moyenne",
                        proposal_date=datetime.utcnow(),
                    )
                )
        return suggestions

    def verify_deliveries(self, tolerance: float = 0.05) -> List[Alert]:
        alerts = []
        for m in self.db.movements.find({"movement_type": "ENTREE"}):
            expected = m["quantity"]
            received = m["quantity"]
            if abs(received - expected) > tolerance * expected:
                alerts.append(
                    Alert(
                        product_id=m["product_id"],
                        alert_type="NON_CONFORMITE_LIVRAISON",
                        message=f"Produit {m['product_id']} livraison non conforme : attendu={expected}, reçu={received}",
                        date=datetime.utcnow(),
                    )
                )
        return alerts
