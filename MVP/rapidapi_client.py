import os
import json
from dotenv import load_dotenv
import requests
from typing import Dict, Optional, Any

# Load environment variables
load_dotenv()

class RapidAPIError(Exception):
    """Custom exception for RapidAPI related errors."""
    pass

class RapidAPIClient:
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.headers = {
            'x-rapidapi-key': self.api_key
        }

    def _make_request(self, url: str, params: Optional[Dict] = None, 
                     method: str = 'GET', data: Optional[Dict] = None, host: Optional[str] = None) -> Dict:
        """Make a generic request to RapidAPI endpoints."""
        try:
            # Add the specific host header for this request
            headers = self.headers.copy()
            if host:
                headers['x-rapidapi-host'] = host

            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            else:  # POST
                response = requests.post(url, headers=headers, data=data)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RapidAPIError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise RapidAPIError("Failed to parse JSON response")
        except Exception as e:
            raise RapidAPIError(f"Unexpected error: {str(e)}")

    # Similarweb endpoints
    def get_similarweb_insights(self, domain: str) -> Dict:
        """Get all insights for a domain."""
        url = "https://similarweb-insights.p.rapidapi.com/all-insights"
        params = {"domain": domain}
        return self._make_request(url, params=params, host="similarweb-insights.p.rapidapi.com")

    def get_similarweb_traffic(self, domain: str) -> Dict:
        """Get traffic data for a domain."""
        url = "https://similarweb-insights.p.rapidapi.com/traffic"
        params = {"domain": domain}
        return self._make_request(url, params=params)

    def get_similarweb_rank(self, domain: str) -> Dict:
        """Get global rank for a domain."""
        url = "https://similarweb-insights.p.rapidapi.com/rank"
        params = {"domain": domain}
        return self._make_request(url, params=params)

    def get_similarweb_similar_sites(self, domain: str) -> Dict:
        """Get similar sites for a domain."""
        url = "https://similarweb-insights.p.rapidapi.com/similar-sites"
        params = {"domain": domain}
        return self._make_request(url, params=params)

    def get_similarweb_seo(self, domain: str) -> Dict:
        """Get SEO data for a domain."""
        url = "https://similarweb-insights.p.rapidapi.com/seo"
        params = {"domain": domain}
        return self._make_request(url, params=params)

    def get_similarweb_website_details(self, domain: str) -> Dict:
        """Get website details for a domain."""
        url = "https://similarweb-insights.p.rapidapi.com/website-details"
        params = {"domain": domain}
        return self._make_request(url, params=params)

    # Instagram endpoints
    def get_instagram_user_by_username(self, username: str) -> Dict:
        """Get Instagram user data by username."""
        url = "https://instagram-premium-api-2023.p.rapidapi.com/v2/user/by/username"
        params = {"username": username}
        return self._make_request(url, params=params, host="instagram-premium-api-2023.p.rapidapi.com")

    def get_instagram_user_medias(self, user_id: str) -> Dict:
        """Get Instagram user medias."""
        url = "https://instagram-premium-api-2023.p.rapidapi.com/v2/user/medias"
        params = {"user_id": user_id}
        return self._make_request(url, params=params)

    def get_instagram_media_comments(self, page_id: str, can_support_threading: bool) -> Dict:
        """Get Instagram media comments."""
        url = "https://instagram-premium-api-2023.p.rapidapi.com/v2/media/comments"
        params = {
            "page_id": page_id,
            "can_support_threading": str(can_support_threading).lower()
        }
        return self._make_request(url, params=params)

    def get_instagram_user_followers(self, user_id: str) -> Dict:
        """Get Instagram user followers."""
        url = "https://instagram-premium-api-2023.p.rapidapi.com/v2/user/followers"
        params = {"user_id": user_id}
        return self._make_request(url, params=params)

    def search_instagram_hashtags(self, query: str) -> Dict:
        """Search Instagram hashtags."""
        url = "https://instagram-premium-api-2023.p.rapidapi.com/v2/search/hashtags"
        params = {"query": query}
        return self._make_request(url, params=params)

    # Facebook endpoints
    def get_facebook_page_posts(self, page_id: str) -> Dict:
        """Get Facebook page posts."""
        url = "https://facebook-scraper3.p.rapidapi.com/page/posts"
        params = {"page_id": page_id}
        return self._make_request(url, params=params)

    def get_facebook_post_comments(self, post_id: str) -> Dict:
        """Get Facebook post comments."""
        url = "https://facebook-scraper3.p.rapidapi.com/post/comments"
        params = {"post_id": post_id}
        return self._make_request(url, params=params)

    def get_facebook_page_reviews(self, page_id: str) -> Dict:
        """Get Facebook page reviews."""
        url = "https://facebook-scraper3.p.rapidapi.com/page/reviews"
        params = {"page_id": page_id}
        return self._make_request(url, params=params)

    def get_facebook_page_details(self, url: str) -> Dict:
        """Get Facebook page details."""
        url = "https://facebook-scraper3.p.rapidapi.com/page/details"
        params = {"url": url}
        return self._make_request(url, params=params, host="facebook-scraper3.p.rapidapi.com")

    # Text Processing endpoints
    def process_sentiment(self, text: str, language: str = "english") -> Dict:
        """Process text sentiment."""
        url = "https://japerk-text-processing.p.rapidapi.com/sentiment/"
        data = {
            "text": text,
            "language": language
        }
        return self._make_request(url, method='POST', data=data, host="japerk-text-processing.p.rapidapi.com")

    def process_stem(self, text: str, language: str = "english", stemmer: str = "porter") -> Dict:
        """Process text stemming."""
        url = "https://japerk-text-processing.p.rapidapi.com/stem/"
        data = {
            "text": text,
            "language": language,
            "stemmer": stemmer
        }
        return self._make_request(url, method='POST', data=data)

    def process_tag(self, text: str, language: str = "english", output: str = "tagged") -> Dict:
        """Process text tagging."""
        url = "https://japerk-text-processing.p.rapidapi.com/tag/"
        data = {
            "text": text,
            "language": language,
            "output": output
        }
        return self._make_request(url, method='POST', data=data)

    def process_phrases(self, text: str, language: str = "english") -> Dict:
        """Process text phrases."""
        url = "https://japerk-text-processing.p.rapidapi.com/phrases/"
        data = {
            "text": text,
            "language": language
        }
        return self._make_request(url, method='POST', data=data)

def main():
    # Example usage
    try:
        client = RapidAPIClient()
        
        # Example: Get Similarweb insights
        similarweb_data = client.get_similarweb_insights("teamtrees.org")
        print("\nSimilarweb Insights:")
        print(json.dumps(similarweb_data, indent=2))
        
        # Example: Get Instagram user data
        instagram_data = client.get_instagram_user_by_username("instagram")
        print("\nInstagram User Data:")
        print(json.dumps(instagram_data, indent=2))
        
        # Example: Get Facebook page details
        facebook_data = client.get_facebook_page_details("https://www.facebook.com/facebook")
        print("\nFacebook Page Details:")
        print(json.dumps(facebook_data, indent=2))
        
        # Example: Process text sentiment
        sentiment_data = client.process_sentiment("I love this product!")
        print("\nText Sentiment:")
        print(json.dumps(sentiment_data, indent=2))
        
    except RapidAPIError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
