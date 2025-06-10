# RapidAPI Client

A Python client for fetching data from various RapidAPI endpoints including Similarweb, Instagram, Facebook, and Text Processing services.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file:
- Copy `.env.example` to `.env`
- Add your RapidAPI credentials

3. Run the client:
```bash
python rapidapi_client.py
```

## Features

- Similarweb:
  - All insights
  - Traffic data
  - Global rank
  - Similar sites
  - SEO data
  - Website details

- Instagram:
  - User data by username
  - User medias
  - Media comments
  - User followers
  - Hashtag search

- Facebook:
  - Page posts
  - Post comments
  - Page reviews
  - Page details

- Text Processing:
  - Sentiment analysis
  - Text stemming
  - Part-of-speech tagging
  - Phrase extraction

## Error Handling

The client includes proper error handling for:
- Network errors
- Invalid API responses
- Missing credentials

## Usage

The client provides a simple interface for making API calls. Each endpoint is wrapped in a dedicated method with proper parameter validation.

Example usage:
```python
client = RapidAPIClient()

# Get Similarweb insights
similarweb_data = client.get_similarweb_insights("teamtrees.org")

# Get Instagram user data
instagram_data = client.get_instagram_user_by_username("instagram")

# Get Facebook page details
facebook_data = client.get_facebook_page_details("https://www.facebook.com/facebook")

# Process text sentiment
sentiment_data = client.process_sentiment("I love this product!")
```
