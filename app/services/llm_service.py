import asyncio
import random


# Mock responses
async def get_llm_response(prompt: str, system_message: str = None) -> str:
    """Return demo answer."""

    print(f"[AI MOCK] Processing prompt: {prompt[:50]}...")
    await asyncio.sleep(1.5)

    prompt_lower = prompt.lower()

    if "blood pressure" in prompt_lower or "bp" in prompt_lower:
        return "Your blood pressure is normal. Still, I recommend monitoring it daily. Water consumption seems adequate."

    if "sleep" in prompt_lower:
        return "Data show a sleep duration under 7 hours. I recommend a stricter sleep routine and avoiding screen time 1 hour before sleep in order to improve sleep quality."

    if "recommendation" in prompt_lower or "clinic" in prompt_lower:
        return "For the symptoms described, I recommend a specialist consultation. Regina Maria clinic is available for Cardiology."

    # Generic answer
    return "Based on provided data, your overall condition is good. I recommend hydration (min 2L daily) and improving physical activity."


async def get_llm_json_response(prompt: str) -> dict:
    """Return simulated JSON response."""
    await asyncio.sleep(1)
    return {"clinic_id": "mock-id-123"}