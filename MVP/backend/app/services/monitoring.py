from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..services.cache import cache_service
from ..services.data_validation import DataValidationService
from ..services.query import QueryService
from ..services.analytics import AnalyticsService
import sentry_sdk
from slack_sdk import WebClient
from pagerduty_sdk import PagerDuty

class MonitoringService:
    def __init__(self, db: Session):
        self.db = db
        self.sentry = sentry_sdk
        self.slack = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.pagerduty = PagerDuty(
            api_key=os.getenv("PAGERDUTY_API_KEY"),
            email=os.getenv("PAGERDUTY_EMAIL")
        )
        self.validation_service = DataValidationService(db)
        self.query_service = QueryService(db)
        self.analytics_service = AnalyticsService(db)

    def initialize_sentry(self):
        """Initialize Sentry SDK."""
        self.sentry.init(
            dsn=os.getenv("SENTRY_DSN"),
            traces_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "development")
        )

    def track_error(self, error: Exception, context: Dict[str, Any] = None):
        """Track error in Sentry."""
        self.sentry.capture_exception(error, context)

    def track_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Track custom metric in Sentry."""
        self.sentry.capture_message(
            f"Metric: {name} = {value}",
            level="info",
            tags=tags
        )

    def send_slack_alert(self, message: str, channel: str = "#alerts"):
        """Send alert to Slack."""
        try:
            self.slack.chat_postMessage(
                channel=channel,
                text=message
            )
        except Exception as e:
            self.track_error(e, {"alert_type": "slack"})

    def send_pagerduty_alert(self, title: str, description: str, severity: str = "critical"):
        """Send alert to PagerDuty."""
        try:
            self.pagerduty.trigger_incident(
                title=title,
                description=description,
                severity=severity
            )
        except Exception as e:
            self.track_error(e, {"alert_type": "pagerduty"})

    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        health = {
            "status": "healthy",
            "checks": [],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Check cache health
        cache_stats = cache_service.get_cache_stats()
        health["checks"].append({
            "name": "cache",
            "status": "healthy" if cache_stats["cache_hits"] > 0 else "warning",
            "details": cache_stats
        })

        # Check database health
        try:
            self.db.execute("SELECT 1").fetchone()
            health["checks"].append({
                "name": "database",
                "status": "healthy",
                "details": {"connection": "success"}
            })
        except Exception as e:
            health["checks"].append({
                "name": "database",
                "status": "critical",
                "details": {"error": str(e)}
            })

        # Check validation status
        validation_status = self.validation_service.get_validation_status()
        health["checks"].append({
            "name": "data_validation",
            "status": "healthy" if validation_status["invalid_records"] == 0 else "warning",
            "details": validation_status
        })

        # Check analytics performance
        try:
            self.analytics_service.get_brand_health(1, datetime.utcnow() - timedelta(days=7), datetime.utcnow())
            health["checks"].append({
                "name": "analytics",
                "status": "healthy",
                "details": {"response": "success"}
            })
        except Exception as e:
            health["checks"].append({
                "name": "analytics",
                "status": "critical",
                "details": {"error": str(e)}
            })

        # Set overall status based on checks
        if any(check["status"] == "critical" for check in health["checks"]):
            health["status"] = "critical"
        elif any(check["status"] == "warning" for check in health["checks"]):
            health["status"] = "warning"

        return health

    def get_alert_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        # TODO: Implement actual alert history storage and retrieval
        return []

    def set_alert_thresholds(self, thresholds: Dict[str, Any]):
        """Set alert thresholds."""
        # TODO: Implement threshold storage and validation
        pass

    def get_current_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts."""
        # TODO: Implement alert tracking
        return []
