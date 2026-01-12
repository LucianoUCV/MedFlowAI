import os
import json
from datetime import date
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("⚠️ EROARE: Verifica .env")

supabase: Client = create_client(url, key)


class SupabaseService:
    def __init__(self):
        self.client = supabase

    def _clean_details(self, details):
        if isinstance(details, dict):
            return details
        if isinstance(details, str):
            try:
                return json.loads(details)
            except:
                return {}
        return {}

    # --- AUTH ---
    def get_user_by_email(self, email: str):
        try:
            res = self.client.table("profiles").select("*").eq("email", email).execute()
            return res.data[0] if res.data else None
        except:
            return None

    def create_user(self, email: str, full_name: str):
        try:
            data = {"email": email, "full_name": full_name}
            res = self.client.table("profiles").insert(data).execute()
            return res.data[0]
        except:
            return {"id": "demo-id", "full_name": full_name}  # Fallback

    # --- DATA ---
    def get_daily_summary(self, user_id: str, target_date: date) -> Dict[str, Any]:
        try:
            # Gather profile
            profile_res = self.client.table("profiles").select("*").eq("id", user_id).execute()
            profile = profile_res.data[0] if profile_res.data else {}

            # Gather data
            res = self.client.table("general").select("*").eq("user_id", user_id).eq("data", str(target_date)).execute()
            raw_data = res.data if res.data else []

            summary = {
                "user_id": user_id,
                "profile": profile,
                "consum": [], "somn": [], "vitale": [], "sport": []
            }

            for record in raw_data:
                cat = record.get("type")
                clean_det = self._clean_details(record.get("details"))

                if cat in summary:
                    summary[cat].append({
                        "id": record.get("id"),
                        "details": clean_det
                    })

            return summary
        except Exception as e:
            print(f"DB Error: {e}")
            return {"user_id": user_id, "consum": [], "somn": [], "vitale": [], "sport": []}

    def add_health_data(self, user_id: str, category: str, data_dict: Dict):
        try:
            if category == 'somn':
                self.client.table("general").delete().eq("user_id", user_id).eq("type", "somn").eq("data",
                                                                                                   str(date.today())).execute()

            payload = {
                "user_id": user_id,
                "data": str(date.today()),
                "type": category,
                "details": json.dumps(data_dict)
            }
            self.client.table("general").insert(payload).execute()
            return True
        except Exception as e:
            print(f"Add Error: {e}")
            return False

    def delete_general_data(self, record_id: str, user_id: str):
        try:
            self.client.table("general").delete().eq("id", record_id).eq("user_id", user_id).execute()
            return True
        except:
            return False

    def get_all_cabinete(self):
        try:
            res = self.client.table("cabinete").select("*").execute()
            return res.data if res.data else []
        except:
            return []


supabase_service = SupabaseService()