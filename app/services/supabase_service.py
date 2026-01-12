import os
import json
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env variables
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("⚠️ EROARE: SUPABASE_URL sau SUPABASE_KEY lipsesc din fișierul .env")

# Initialize Supabase client
supabase: Client = create_client(url, key)


class SupabaseService:
    def __init__(self):
        self.client = supabase

    # ==================== AUTH / PROFILES ====================

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Search a user by email."""
        try:
            response = self.client.table("profiles").select("*").eq("email", email).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error searching user: {e}")
            return None

    def create_user(self, email: str, full_name: str) -> Dict:
        """Create a new user (automated registration)."""
        try:
            data = {
                "email": email,
                "full_name": full_name,
            }
            response = self.client.table("profiles").insert(data).execute()
            return response.data[0]
        except Exception as e:
            print(f"Error creating user: {e}")
            raise e

    def get_profile_by_id(self, user_id: str) -> Dict:
        """Take profile data by id (for Home Page)."""
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"Error get_profile: {e}")
            return {}

    # ==================== HEALTH DATA (DASHBOARD) ====================

    def get_daily_summary(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """
        Extract all health data for today.
        For home page progress.
        """
        try:
            # 1. Take profile
            profile = self.get_profile_by_id(user_id)

            # 2. Take data from "general" table
            response = self.client.table("general") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("data", str(target_date)) \
                .execute()

            raw_data = response.data if response.data else []

            # 3. Organize data in categories
            summary = {
                "user_id": user_id,
                "profile": profile,
                "date": str(target_date),
                "consum": [],
                "somn": [],
                "vitale": [],
                "sport": [],
                "medicamente": []
            }

            for record in raw_data:
                category = record.get("type")  # consum, somn, etc...
                details = record.get("details")

                if isinstance(details, str):
                    try:
                        details = json.loads(details)
                    except:
                        details = {}

                if category in summary:
                    summary[category].append(details)

            return summary

        except Exception as e:
            print(f"Error generating daily summary: {e}")
            return {
                "user_id": user_id,
                "consum": [], "somn": [], "vitale": [], "sport": []
            }

    def add_health_data(self, user_id: str, category: str, data_dict: Dict):
        """Add new entry (Add Data Page)."""
        try:
            payload = {
                "user_id": user_id,
                "data": str(date.today()),
                "type": category,
                "details": json.dumps(data_dict)
            }
            self.client.table("general").insert(payload).execute()
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    # ==================== SCHEDULE / CABINETE ====================

    def get_all_cabinete(self) -> List[Dict]:
        """Return clinics list."""
        try:
            response = self.client.table("cabinete").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting clinics: {e}")
            return []

    def create_appointment(self, user_id: str, cabinet_id: str):
        """Create reservation (Demo)."""
        try:
            payload = {
                "user_id": user_id,
                "cabinet_id": cabinet_id,
                "data": datetime.now().isoformat(),
                "active": True
            }
            self.client.table("programari").insert(payload).execute()
            return True
        except Exception as e:
            print(f"Error creating reservation: {e}")
            return False


supabase_service = SupabaseService()