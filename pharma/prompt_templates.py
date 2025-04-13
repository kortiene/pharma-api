from typing import List

from pharma.models import Alert, ForecastResult, KPIReport, PurchaseProposal


def prompt_forecast(forecasts: List[ForecastResult]) -> str:
    lines = [
        f"- {f.product_id} : {f.suggested_quantity} unités à prévoir"
        for f in forecasts
    ]
    return (
        "Voici les prévisions de consommation à analyser :\n"
        + "\n".join(lines)
        + "\nExplique quels produits sont à risque de rupture et pourquoi."
    )


def prompt_alerts(alerts: List[Alert]) -> str:
    lines = [f"{a.alert_type} – {a.product_id} : {a.message}" for a in alerts]
    return (
        "Voici les alertes détectées par le système :\n"
        + "\n".join(lines)
        + "\nReformule ces alertes en langage clair à destination du pharmacien."
    )


def prompt_inventory_audit(alerts: List[Alert]) -> str:
    if not alerts:
        return "Aucun écart d'inventaire détecté. Que peut-on en conclure ?"
    lines = [f"- {a.product_id} : {a.message}" for a in alerts]
    return (
        "Suite à un audit d'inventaire, les écarts suivants ont été identifiés :\n"
        + "\n".join(lines)
        + "\nQuels sont les risques et les recommandations ?"
    )


def prompt_kpi_report(kpis: KPIReport) -> str:
    return (
        f"Voici les KPI du mois :\n"
        f"- Total de ruptures : {kpis.total_ruptures}\n"
        f"- Total des sorties : {kpis.total_exits}\n"
        f"- Top produits : {', '.join(kpis.top_products)}\n"
        "Rédige un rapport synthétique et interprétatif pour le pharmacien."
    )


def prompt_purchase_suggestions(proposals: List[PurchaseProposal]) -> str:
    if not proposals:
        return "Aucune suggestion de commande n’a été générée. Est-ce normal ?"
    lines = [
        f"{p.product_id} : {p.suggested_quantity} unités proposées – Justification : {p.justification}"
        for p in proposals
    ]
    return (
        "Voici les suggestions de commande générées automatiquement :\n"
        + "\n".join(lines)
        + "\nValide ou ajuste ces suggestions selon les bonnes pratiques de gestion de stock."
    )


def prompt_delivery_verification(alerts: List[Alert]) -> str:
    if not alerts:
        return "Toutes les livraisons sont conformes. Peut-on valider la clôture de ce lot ?"
    lines = [f"- {a.product_id} : {a.message}" for a in alerts]
    return (
        "Des non-conformités ont été détectées dans les livraisons :\n"
        + "\n".join(lines)
        + "\nComment faut-il réagir face à ces anomalies ?"
    )


def prompt_conversational(message: str, context: dict) -> str:
    forecast = context.get("forecast", [])
    alerts = context.get("alerts", [])
    summary = (
        "\n".join(
            [
                f"- {f['product_id']}: {f['suggested_quantity']} unités à commander"
                for f in forecast
            ]
        )
        if forecast
        else "Aucune prévision critique."
    )

    alert_texts = (
        "\n".join(
            [
                f"- {a['product_id']} ({a['alert_type']}) : {a['message']}"
                for a in alerts
            ]
        )
        if alerts
        else "Aucune alerte active."
    )

    return (
        f"Voici l’état du système :\n"
        f"Prévisions :\n{summary}\n\n"
        f"Alertes :\n{alert_texts}\n\n"
        f"Message du pharmacien : {message}\n"
        f"Donne une réponse claire, contextualisée et en français."
    )
