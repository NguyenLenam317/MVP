import time
from typing import Optional, Dict, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from ..database.config import get_db
from ..models.audit import AuditLog

class RateLimitException(Exception):
    """Raised when rate limit is exceeded."""
    pass

class APIException(Exception):
    """Raised when API returns an error."""
    pass

class GlobalTokenBucket:
    def __init__(self, max_rate: int, per_seconds: int):
        self.max_rate = max_rate
        self.per_seconds = per_seconds
        self.tokens = max_rate
        self.last_refill = time.time()
        
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * (self.max_rate / self.per_seconds)
        self.tokens = min(self.max_rate, self.tokens + tokens_to_add)
        self.last_refill = now
        
    def acquire_token(self):
        self._refill()
        if self.tokens < 1:
            raise RateLimitException("Rate limit exceeded")
        self.tokens -= 1

class BaseAdapter:
    def __init__(self, api_key: str, api_host: str):
        self.api_key = api_key
        self.api_host = api_host
        self.session = requests.Session()
        self.rate_limiter = GlobalTokenBucket(max_rate=2, per_seconds=1)  # 2/sec
        self._setup_session()

    def _setup_session(self):
        self.session.headers.update({
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        })

    def _rate_limit_guard(self):
        """Ensure rate limits are respected."""
        try:
            self.rate_limiter.acquire_token()
        except RateLimitException as e:
            self._log_audit(
                action=f"rate_limit_{self.__class__.__name__}",
                details={"error": str(e)}
            )
            raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda _: None
    )
    def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        self._rate_limit_guard()
        try:
            resp = self.session.request(method, url, **kwargs)
            if resp.status_code == 429:
                # Handle rate limit (exponential backoff, retry)
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    time.sleep(int(retry_after))
                raise RateLimitException("429 Too Many Requests")
            elif not resp.ok:
                # Log and escalate error
                self._log_audit(
                    action=f"api_error_{self.__class__.__name__}",
                    details={
                        "status": resp.status_code,
                        "response": resp.text
                    }
                )
                raise APIException(f"API error: {resp.status_code} {resp.text}")
            
            return resp.json()
        except Exception as e:
            self._log_audit(
                action=f"request_error_{self.__class__.__name__}",
                details={"error": str(e)}
            )
            raise

    def _log_audit(self, action: str, details: Dict[str, Any]):
        db = next(get_db())
        try:
            audit_log = AuditLog(
                action=action,
                details=details,
                ip_address="127.0.0.1",  # TODO: Get from request context
                user_agent="API Adapter"
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            print(f"Failed to log audit: {e}")
            db.rollback()
