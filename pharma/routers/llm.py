# app/api/router1.py
from fastapi import APIRouter
from pharma.prompt_templates import (
    prompt_alerts,
    prompt_delivery_verification,
    prompt_forecast,
    prompt_inventory_audit,
    prompt_kpi_report,
    prompt_purchase_suggestions,
    prompt_conversational
)

from openai import OpenAI
from pharma.models import ChatRequest
from pharma.services.agent import SmartInventoryAgent
import os


router = APIRouter(prefix="/llm", tags=["Assistant LLM"])


ag = SmartInventoryAgent()

# Set your OpenAI API key
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_response(
        prompt: str,
        system_prompt: str = "Tu es un assistant pharmacien intelligent."
) -> str:
    # Format the prompt for a conversational AI system
    formatted_prompt = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": prompt.strip()},
    ]
    
    try:
        # Make the API call using the chat model (e.g., gpt-3.5-turbo or gpt-4)
        response = llm.chat.completions.create(
            model="gpt-4",  # Use gpt-4 for more advanced responses
            messages=formatted_prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.95,
            stop=["</s>"]  # If you want to use a stop sequence (adjust as needed)
        )
        
        # Extract and return the assistant's response
        assistant_response = response.choices[0].message.content
        return assistant_response.strip()

    except Exception as e:
        # Handle OpenAI API errors (e.g., rate limit, network issues)
        print(f"An error occurred: {e}")
        return "Sorry, I encountered an error. Please try again later."


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
