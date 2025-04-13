from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, conint

# --- MODELES Pydantic ---


class Product(BaseModel):
    id: str
    name: str
    category: str
    dosage: Optional[str] = None
    batch_number: Optional[str]
    expiration_date: date
    unit_price: float
    supplier: Optional[str] = None
    regulatory_class: Optional[Literal["Ordinaire", "Stupéfiant", "Psychotrope"]] = (
        "Ordinaire"
    )


class StockItem(BaseModel):
    product_id: str
    quantity: conint(ge=0)
    last_update: datetime
    location: Optional[str] = "Magasin principal"


class StockThreshold(BaseModel):
    product_id: str
    minimum_stock: int
    critical_stock: int


class ConsumptionForecast(BaseModel):
    product_id: str
    predicted_quantity: int
    forecast_start: date
    forecast_end: date
    model_used: Optional[str] = "SMA"


class StockAlert(BaseModel):
    product_id: str
    alert_type: Literal["RUPTURE", "PEREMPTION", "SURSTOCK", "SEUIL_CRITIQUE"]
    message: str
    date_triggered: datetime
    severity: Literal["INFO", "WARNING", "CRITICAL"]


class PurchaseProposal(BaseModel):
    product_id: str
    suggested_quantity: int
    based_on: Literal["Prévision", "Seuil", "Manuel"]
    justification: str
    proposal_date: datetime


class StockMovement(BaseModel):
    movement_type: Literal["ENTREE", "SORTIE", "TRANSFERT", "RETOUR", "RUPTURE"]
    product_id: str
    quantity: int
    date: datetime
    reason: Optional[str]
    destination: Optional[str] = None


class InventoryResult(BaseModel):
    product_id: str
    expected_quantity: int
    counted_quantity: int
    discrepancy: int
    inventory_date: date
    responsible_user: Optional[str]


class ForecastResult(BaseModel):
    product_id: str
    average_consumption: float
    suggested_quantity: int


class Alert(BaseModel):
    product_id: str
    alert_type: str
    message: str
    date: datetime


class KPIReport(BaseModel):
    total_ruptures: int
    total_exits: int
    top_products: List[str]
