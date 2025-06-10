from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.canonical import Brand, TrafficSnapshot, SEOInfo, SocialPost, Review, SentimentResult
from ..services.cache import cache_service
import pandas as pd
import numpy as np
from scipy import stats

class DataValidationService:
    def __init__(self, db: Session):
        self.db = db
        self.validation_rules = {
            "traffic": {
                "visits": {
                    "min": 0,
                    "max": 1000000,
                    "z_threshold": 3.0
                },
                "bounce_rate": {
                    "min": 0.0,
                    "max": 1.0
                },
                "avg_visit_duration": {
                    "min": 0.0,
                    "max": 3600.0
                }
            },
            "social": {
                "engagement": {
                    "min": 0,
                    "max": 10000
                },
                "sentiment_score": {
                    "min": -1.0,
                    "max": 1.0
                }
            },
            "reviews": {
                "rating": {
                    "min": 0.0,
                    "max": 5.0
                },
                "sentiment_score": {
                    "min": -1.0,
                    "max": 1.0
                }
            }
        }

    def validate_data(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Validate incoming data against rules."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        if data_type not in self.validation_rules:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Unknown data type: {data_type}")
            return validation_results

        rules = self.validation_rules[data_type]
        
        for field, rule in rules.items():
            if field in data:
                value = data[field]
                
                # Check min/max
                if "min" in rule and value < rule["min"]:
                    validation_results["valid"] = False
                    validation_results["errors"].append(
                        f"{field} value {value} below minimum {rule['min']}")
                
                if "max" in rule and value > rule["max"]:
                    validation_results["valid"] = False
                    validation_results["errors"].append(
                        f"{field} value {value} above maximum {rule['max']}")

        return validation_results

    def detect_anomalies(self, brand_id: int, data_type: str) -> Dict[str, Any]:
        """Detect anomalies in historical data."""
        if data_type == "traffic":
            data = self.db.query(TrafficSnapshot).filter(
                TrafficSnapshot.brand_id == brand_id
            ).all()
        elif data_type == "social":
            data = self.db.query(SocialPost).filter(
                SocialPost.brand_id == brand_id
            ).all()
        elif data_type == "reviews":
            data = self.db.query(Review).filter(
                Review.brand_id == brand_id
            ).all()
        else:
            return {
                "valid": False,
                "errors": ["Unknown data type"]
            }

        df = pd.DataFrame([d.__dict__ for d in data])
        anomalies = []

        # Check for outliers using Z-score
        for field in self.validation_rules[data_type]:
            if field in df.columns:
                z_scores = np.abs(stats.zscore(df[field]))
                outliers = df[z_scores > self.validation_rules[data_type][field].get("z_threshold", 3.0)]
                if not outliers.empty:
                    anomalies.extend(outliers.to_dict("records"))

        return {
            "valid": len(anomalies) == 0,
            "anomalies": anomalies
        }

    def detect_duplicates(self, brand_id: int, data_type: str) -> Dict[str, Any]:
        """Detect duplicate records."""
        if data_type == "traffic":
            data = self.db.query(TrafficSnapshot).filter(
                TrafficSnapshot.brand_id == brand_id
            ).all()
        elif data_type == "social":
            data = self.db.query(SocialPost).filter(
                SocialPost.brand_id == brand_id
            ).all()
        elif data_type == "reviews":
            data = self.db.query(Review).filter(
                Review.brand_id == brand_id
            ).all()
        else:
            return {
                "valid": False,
                "errors": ["Unknown data type"]
            }

        df = pd.DataFrame([d.__dict__ for d in data])
        duplicates = df[df.duplicated(
            subset=["timestamp", "source"],
            keep=False
        )]

        return {
            "valid": len(duplicates) == 0,
            "duplicates": duplicates.to_dict("records")
        }

    def quarantine_invalid_data(self, invalid_data: List[Dict[str, Any]], data_type: str):
        """Quarantine invalid data."""
        # TODO: Implement actual quarantine logic
        # This could involve:
        # - Moving data to a quarantine table
        # - Adding metadata about why it was quarantined
        # - Notifying administrators
        pass

    def get_validation_status(self) -> Dict[str, Any]:
        """Get overall validation status."""
        status = {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "anomalies": 0,
            "duplicates": 0,
            "last_check": datetime.utcnow().isoformat()
        }

        # Check traffic
        traffic_status = self.detect_anomalies(None, "traffic")
        status["invalid_records"] += len(traffic_status["anomalies"])

        # Check social
        social_status = self.detect_anomalies(None, "social")
        status["invalid_records"] += len(social_status["anomalies"])

        # Check reviews
        reviews_status = self.detect_anomalies(None, "reviews")
        status["invalid_records"] += len(reviews_status["anomalies"])

        return status

    def get_cleanup_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggestions for data cleanup."""
        suggestions = []

        # Check for duplicates
        for data_type in ["traffic", "social", "reviews"]:
            duplicates = self.detect_duplicates(None, data_type)
            if duplicates["duplicates"]:
                suggestions.append({
                    "type": "duplicates",
                    "data_type": data_type,
                    "count": len(duplicates["duplicates"]),
                    "action": "remove_older_duplicates"
                })

        # Check for anomalies
        for data_type in ["traffic", "social", "reviews"]:
            anomalies = self.detect_anomalies(None, data_type)
            if anomalies["anomalies"]:
                suggestions.append({
                    "type": "anomalies",
                    "data_type": data_type,
                    "count": len(anomalies["anomalies"]),
                    "action": "quarantine"
                })

        return suggestions
