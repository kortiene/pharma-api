from fastapi import APIRouter
from pharma.services.agent import SmartInventoryAgent


router = APIRouter(prefix="/agent", tags=["Agents"])
ag = SmartInventoryAgent()


@router.get("/forecast")
def get_forecast():
    return ag.forecast_consumption()


@router.get("/alerts/critical")
def get_critical_alerts():
    return ag.detect_critical_stocks()


@router.get("/alerts/expiry")
def get_expiry_alerts():
    return ag.detect_expiring_products()


@router.get("/audit")
def get_inventory_audit():
    return ag.simulate_inventory_audit()


@router.get("/kpis")
def get_kpi():
    return ag.generate_kpi_report()


@router.get("/proposals")
def get_proposals():
    return ag.suggest_purchase_orders()


@router.get("/deliveries")
def get_delivery_verification():
    return ag.verify_deliveries()
