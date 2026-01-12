import asyncio
import random


async def get_llm_response(prompt: str, summary_data: dict = None, current_score: int = 0,
                           is_chat: bool = False) -> str:
    await asyncio.sleep(1.0)

    data = {
        "water": 0, "meals": 0, "sleep": 0, "sport": 0, "bp": "N/A"
    }

    if summary_data:
        for x in summary_data.get('consum', []):
            d = x.get('details', {}) if isinstance(x.get('details'), dict) else {}
            data["water"] += int(d.get('lichide_ml', 0) or 0)
            data["meals"] += int(d.get('mese', 0) or 0)

        if summary_data.get('somn'):
            d = summary_data['somn'][0].get('details', {}) if isinstance(summary_data['somn'][0].get('details'),
                                                                         dict) else {}
            data["sleep"] = float(d.get('ore_somn', 0) or 0)

        for x in summary_data.get('sport', []):
            d = x.get('details', {}) if isinstance(x.get('details'), dict) else {}
            data["sport"] += int(d.get('durata', 0) or 0)

    prompt_lower = prompt.lower()

    # --- AI CHAT ---
    if is_chat:
        # Case: HEAD HURTS
        if "head" in prompt_lower and "hurt" in prompt_lower:
            reasons = []
            if data["water"] < 1500: reasons.append(f"you only drank {data['water']}ml of water (target 2000ml)")
            if data["sleep"] < 6 and data["sleep"] > 0: reasons.append(f"you only slept {data['sleep']} hours")
            if data["meals"] < 2: reasons.append("you haven't eaten enough meals")

            if reasons:
                return f"I see you have a headache. Looking at your data, it might be because {' and '.join(reasons)}. Please hydrate and rest."
            return "Your logs look okay (hydration and sleep are good). If the headache persists, it might be stress or vision related. Take a break from screens."

        # Case: STOMACH HURTS
        if "stomach" in prompt_lower:
            if data[
                "meals"] > 4: return "You logged quite a few meals today. It might be indigestion from overeating. Try some tea."
            if data[
                "meals"] == 0: return "You haven't logged any food today! Taking medication or drinking coffee on an empty stomach can cause pain. Please eat something light."
            return "Stomach pain can have many causes. Avoid spicy food for the rest of the day and stay hydrated."

        # Case: NOT FEELING GOOD
        if "good" in prompt_lower and "feel" in prompt_lower:
            if data[
                "sport"] == 0: return "You haven't moved much today (0 min activity). A short 10-minute walk often helps with general malaise."
            if data[
                "water"] < 1000: return "Dehydration often causes a general bad feeling. You are low on water today. Drink a glass now."
            return "I'm sorry to hear that. Your vitals seem stable based on logs. Rest for a bit and monitor your temperature."

        # Case: FAT / WEIGHT
        if "fat" in prompt_lower or "weight" in prompt_lower:
            if data[
                "sport"] < 30: return f"Weight management requires consistency. You only did {data['sport']} min of activity today. Try to hit at least 30 minutes."
            return "You are doing well with activity! Weight loss takes time. Focus on balanced meals (you logged " + str(
                data["meals"]) + " today)."

        # Case: EXHAUSTED
        if "tired" in prompt_lower or "exhausted" in prompt_lower:
            if data[
                "sleep"] < 7: return f"It's no surprise you are exhausted. You only slept {data['sleep']} hours. Please prioritize getting to bed early tonight."
            return "You slept enough, so this might be mental fatigue or dehydration. Check your water intake."

        # GENERIC CHAT
        return "I am analyzing your data... Based on your logs, keep maintaining your hydration and sleep schedule. How else can I help?"

    # --- Daily Summary ---
    else:
        return f"""**Health Analysis Summary**

Based on your current data, here is the breakdown:

**Positive Points:**
- **Hydration:** {data['water']}ml recorded.
- **Activity:** {data['sport']} mins of movement.

**Areas for Improvement:**
- **Sleep:** {data['sleep']}h. (Target: 7h+)
- **Nutrition:** {data['meals']} meals logged.

**Recommendations:**
1. {'Drink more water to hit 2L.' if data['water'] < 2000 else 'Keep up the hydration!'}
2. {'Try to sleep earlier tonight.' if data['sleep'] < 7 else 'Maintain this sleep schedule.'}

**Overall health score: {current_score}/100**"""


async def get_llm_json_response(prompt: str) -> dict:
    await asyncio.sleep(0.5)
    return {"clinic_id": "mock-id-123"}