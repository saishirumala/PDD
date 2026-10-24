import httpx
import logging
from typing import Dict, Any, Tuple
from config import settings

logger = logging.getLogger("nutriguide.supabase")

class SupabaseService:
    def _clean_key(self, key_val: str) -> str:
        if not key_val:
            return ""
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

supabase_service = SupabaseService()
