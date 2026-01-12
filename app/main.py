from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.services.supabase_service import supabase_service
from app.services.llm_service import get_llm_response
from datetime import date
import json

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")


def get_current_user(request: Request):
    return request.cookies.get("user_id")


# --- LOGIN ---
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if get_current_user(request): return RedirectResponse("/home")
    return RedirectResponse("/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_submit(email: str = Form(...), name: str = Form(...)):
    user = supabase_service.get_user_by_email(email)
    if not user: user = supabase_service.create_user(email, name)
    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(key="user_id", value=user['id'])
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_id")
    return response


def calculate_daily_stats(summary):
    c_list = summary.get('consum', [])
    meals = sum([int(x['details'].get('mese', 0) or 0) for x in c_list])
    water_ml = sum([int(x['details'].get('lichide_ml', 0) or 0) for x in c_list])

    s_list = summary.get('somn', [])
    sleep_hours = float(s_list[0]['details'].get('ore_somn', 0) or 0) if s_list else 0

    sp_list = summary.get('sport', [])
    sport_min = sum([int(x['details'].get('durata', 0) or 0) for x in sp_list])

    v_list = summary.get('vitale', [])
    has_vitals = len(v_list) > 0
    bp = v_list[0]['details'].get('tensiune', '-') if has_vitals else '-'

    # 1. Water (Target 2000ml) -> Max 25 pct
    water_score = min(25, (water_ml / 2000) * 25)

    # 2. Meals (Target 3 meals) -> Max 20 pct
    meal_score = min(20, (meals / 3) * 20)

    # 3. Sleep (Target 7-9h) -> Max 30 pct
    if sleep_hours >= 7:
        sleep_score = 30
    elif sleep_hours >= 5:
        sleep_score = 15
    elif sleep_hours > 0:
        sleep_score = 5
    else:
        sleep_score = 0

    # 4. Sport (Target 30 min) -> Max 15 pct
    sport_score = min(15, (sport_min / 30) * 15)

    # 5. Vitals (Bonus logging) -> 10 pct
    vital_score = 10 if has_vitals else 0

    total_score = int(water_score + meal_score + sleep_score + sport_score + vital_score)

    return {
        "score": total_score,
        "meals": meals, "water": water_ml,
        "sleep": sleep_hours, "sport": sport_min, "bp": bp
    }


# --- HOME ---
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, user_id: str = Depends(get_current_user)):
    if not user_id: return RedirectResponse("/login")

    summary = supabase_service.get_daily_summary(user_id, date.today())
    profile = summary.get('profile', {}) or {}

    stats = calculate_daily_stats(summary)

    consum_txt = f"{stats['meals']} meals, {stats['water'] / 1000}L water" if (
                stats['meals'] or stats['water']) else "No data"
    somn_txt = f"{stats['sleep']}h recorded" if stats['sleep'] else "No data"
    vitale_txt = f"BP: {stats['bp']}" if stats['bp'] != '-' else "No data"
    sport_txt = f"{stats['sport']}min activity" if stats['sport'] else "No data"

    return templates.TemplateResponse("home.html", {
        "request": request,
        "name": profile.get('full_name', 'User'),
        "user_id": user_id,
        "score": stats['score'],
        "consum_txt": consum_txt,
        "somn_txt": somn_txt,
        "vitale_txt": vitale_txt,
        "sport_txt": sport_txt
    })


# --- API ---
@app.get("/api/v1/generate_alert")
async def generate_alert_api(user_id: str = Depends(get_current_user)):
    summary = supabase_service.get_daily_summary(user_id, date.today())
    stats = calculate_daily_stats(summary)

    feedback = await get_llm_response("Analiza", summary_data=summary, current_score=stats['score'])
    return {"feedback": feedback}


@app.post("/ask")
async def ask_api(request: Request, user_id: str = Depends(get_current_user)):
    form = await request.form()
    summary = supabase_service.get_daily_summary(user_id, date.today())
    ans = await get_llm_response(form.get("question"), summary_data=summary, is_chat=True)
    return {"generated_feedback": ans}


@app.post("/api/v1/add_health_data")
async def add_data_api(request: Request, user_id: str = Depends(get_current_user)):
    data = await request.json()
    res = supabase_service.add_health_data(user_id, data['category'], data['data'])
    return {"success": res}


@app.get("/api/v1/today_data")
async def today_data_api(user_id: str = Depends(get_current_user)):
    return supabase_service.get_daily_summary(user_id, date.today())


@app.post("/api/v1/delete_data")
async def delete_data_api(request: Request, user_id: str = Depends(get_current_user)):
    data = await request.json()
    res = supabase_service.delete_general_data(data['id'], user_id)
    return {"success": res}


@app.get("/api/v1/cabinete")
async def get_cabinete_api():
    return {"cabinete": supabase_service.get_all_cabinete()}


@app.get("/add-data", response_class=HTMLResponse)
async def p1(request: Request): return templates.TemplateResponse("add-data.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def p2(request: Request): return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/schedule", response_class=HTMLResponse)
async def p3(request: Request): return templates.TemplateResponse("schedule.html", {"request": request})