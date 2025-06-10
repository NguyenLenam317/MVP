from typing import Dict, Any, Optional
from .base import BaseAdapter

class JaperkNLPAdapter(BaseAdapter):
    BASE_URL = "https://japerk-text-processing.p.rapidapi.com/"

    def __init__(self, api_key: str, api_host: str):
        super().__init__(api_key, api_host)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        })

    def fetch_sentiment(self, text: str, language: str = "english") -> Dict[str, Any]:
        data = {"text": text, "language": language}
        return self._request("POST", self.BASE_URL + "sentiment/", data=data)

    def fetch_stem(self, text: str, language: str = "english", stemmer: str = "porter") -> Dict[str, Any]:
        data = {"text": text, "language": language, "stemmer": stemmer}
        return self._request("POST", self.BASE_URL + "stem/", data=data)

    def fetch_tag(self, text: str, language: str = "english", output: str = "tagged") -> Dict[str, Any]:
        data = {"text": text, "language": language, "output": output}
        return self._request("POST", self.BASE_URL + "tag/", data=data)

    def fetch_phrases(self, text: str, language: str = "english") -> Dict[str, Any]:
        data = {"text": text, "language": language}
        return self._request("POST", self.BASE_URL + "phrases/", data=data)

    def normalize_sentiment(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize sentiment analysis results."""
        if not raw_data.get("success"):
            return {"score": 0.0, "label": "neutral"}
            
        return {
            "score": raw_data.get("probability", 0.0),
            "label": raw_data.get("label", "neutral"),
            "timestamp": int(time.time())
        }
