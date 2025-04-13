# app/api/router1.py
from fastapi import APIRouter
from pharma.prompt_templates import (prompt_alerts, prompt_delivery_verification,
                              prompt_forecast, prompt_inventory_audit,
                              prompt_kpi_report, prompt_purchase_suggestions, prompt_conversational)
from llama_cpp import Llama
from pharma.models import ChatRequest
from pharma.services.agent import SmartInventoryAgent
import os


router = APIRouter(prefix="/llm", tags=["Assistant LLM"])


# Load the model (make sure the path and quantized model are correct)
MODEL_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/llm_models/openelm-3b-instruct-q2_k.gguf"


llm = Llama(
    model_path=MODEL_PATH,  # Adapt path to your system
    n_ctx=2048,  # Contexte étendu (utile pour les prompts longs)
    n_threads=8,  # 2 threads par cœur sur ton quad-core = 8 threads
    use_mlock=True,  # Évite le swap, garde le modèle en mémoire
    n_batch=64,  # Taille de batch raisonnable pour équilibre vitesse/mémoire
    verbose=False,  # Réduit le bruit dans la console
)


ag = SmartInventoryAgent()


def generate_response(
    prompt: str, system_prompt: str = "Tu es un assistant pharmacien intelligent."
) -> str:
    formatted_prompt = (
        f"<|system|>\n{system_prompt.strip()}\n"
        f"<|user|>\n{prompt.strip()}\n"
        f"<|assistant|>"
    )

    result = llm(
        formatted_prompt, max_tokens=512, temperature=0.7, top_p=0.95, stop=["</s>"]
    )

    return result["choices"][0]["text"].strip()


@router.post("/chat")
def chat(request: ChatRequest):
    forecast = [f.dict() for f in ag.forecast_consumption()]
    alerts = [a.dict() for a in ag.detect_critical_stocks() + ag.detect_expiring_products()]
    
    prompt = prompt_conversational(request.message, {"forecast": forecast, "alerts": alerts})
    reply = generate_response(prompt)
    return {"prompt": prompt, "response": reply}


@router.get("/forecast")
def explain_forecast():
    forecasts = ag.forecast_consumption()
    prompt = prompt_forecast(forecasts)
    return {"prompt": prompt, "response": generate_response(prompt)}


@router.get("/kpi")
def explain_kpi():
    kpis = ag.generate_kpi_report()
    prompt = prompt_kpi_report(kpis)
    return {"prompt": prompt, "response": generate_response(prompt)}


@router.get("/alerts")
def humanize_alerts():
    alerts = ag.detect_critical_stocks() + ag.detect_expiring_products()
    prompt = prompt_alerts(alerts)
    return {"prompt": prompt, "response": generate_response(prompt)}


@router.get("/inventory")
def audit_explanation():
    audit_alerts = ag.simulate_inventory_audit()
    prompt = prompt_inventory_audit(audit_alerts)
    return {"prompt": prompt, "response": generate_response(prompt)}


@router.get("/purchase")
def explain_proposals():
    proposals = ag.suggest_purchase_orders()
    prompt = prompt_purchase_suggestions(proposals)
    return {"prompt": prompt, "response": generate_response(prompt)}


@router.get("/delivery")
def explain_deliveries():
    alerts = ag.verify_deliveries()
    prompt = prompt_delivery_verification(alerts)
    return {"prompt": prompt, "response": generate_response(prompt)}
