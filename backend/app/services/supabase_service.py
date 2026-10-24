import httpx
import logging
from typing import Dict, Any, Tuple
from app.config import settings

logger = logging.getLogger("nutriguide.supabase")

class SupabaseService:
    def _clean_key(self, key_val: str) -> str:
        if not key_val:
            return ""
        # Check if key is ASCII (not a masked placeholder with bullet characters)
        try:
            key_val.encode("ascii")
            return key_val.strip()
        except UnicodeEncodeError:
            return ""

    @property
    def url(self) -> str:
        return settings.SUPABASE_URL.rstrip('/') if settings.SUPABASE_URL else ""

    @property
    def key(self) -> str:
        clean_secret = self._clean_key(settings.SUPABASE_SECRET_KEY or "")
        clean_pub = self._clean_key(settings.SUPABASE_PUBLISHABLE_KEY or "")
        return clean_secret or clean_pub

    def is_configured(self) -> bool:
        return bool(self.url and self.key)

    def test_connection(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Tests connection to the Supabase REST API endpoint.
        Returns (success: bool, message: str, details: dict)
        """
        if not self.url:
            return False, "SUPABASE_URL is not set", {}
        if not self.key:
            return False, "Neither SUPABASE_SECRET_KEY nor SUPABASE_PUBLISHABLE_KEY is set", {}

        health_url = f"{self.url}/rest/v1/"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(health_url, headers=headers)
                if response.status_code in (200, 204):
                    return True, "Successfully connected to Supabase REST API (Service Role Key verified)!", {
                        "status_code": response.status_code,
                        "url": self.url
                    }
                elif response.status_code == 401 and "Secret API key required" in response.text:
                    return True, "Supabase REST API endpoint reachable! (Using Publishable Key; full admin API operations require unmasked SUPABASE_SECRET_KEY)", {
                        "status_code": response.status_code,
                        "url": self.url,
                        "key_type": "Publishable Key",
                        "hint": "Set full unmasked SUPABASE_SECRET_KEY in .env for full service access"
                    }
                else:
                    return True, f"Supabase endpoint reached (HTTP {response.status_code})", {
                        "status_code": response.status_code,
                        "url": self.url,
                        "response": response.text[:200]
                    }
        except httpx.ConnectError as exc:
            return False, f"Could not reach Supabase endpoint at {self.url}: {exc}", {}
        except Exception as exc:
            return False, f"Supabase connection test failed: {str(exc)}", {}

    def sync_user_registration(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Attempts to sync a newly registered user to the Supabase REST API `users` table.
        """
        if not self.is_configured():
            return False, "Supabase service not configured"

        endpoint = f"{self.url}/rest/v1/users"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        payload = {
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "password_hash": user_data.get("password_hash"),
            "calorie_goal": user_data.get("calorie_goal", 2000),
            "protein_goal": user_data.get("protein_goal", 150.0),
            "carbs_goal": user_data.get("carbs_goal", 225.0),
            "fat_goal": user_data.get("fat_goal", 65.0),
            "fiber_goal": user_data.get("fiber_goal", 30.0)
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(endpoint, headers=headers, json=payload)
                if resp.status_code in (200, 201, 204):
                    logger.info(f"Successfully synced user {user_data.get('email')} to Supabase REST API.")
                    return True, "Synced to Supabase"
                else:
                    logger.warning(f"Supabase REST user sync returned HTTP {resp.status_code}: {resp.text}")
                    return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as exc:
            logger.error(f"Failed to sync user to Supabase REST API: {exc}")
            return False, str(exc)

supabase_service = SupabaseService()
