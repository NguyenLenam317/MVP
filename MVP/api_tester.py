import streamlit as st
from rapidapi_client import RapidAPIClient
import json
from typing import Dict, Any

# Initialize the client
client = RapidAPIClient()

# Define endpoint configurations
ENDPOINTS = {
    "Similarweb": {
        "All Insights": {
            "function": client.get_similarweb_insights,
            "params": ["domain"]
        },
        "Traffic": {
            "function": client.get_similarweb_traffic,
            "params": ["domain"]
        },
        "Rank": {
            "function": client.get_similarweb_rank,
            "params": ["domain"]
        },
        "Similar Sites": {
            "function": client.get_similarweb_similar_sites,
            "params": ["domain"]
        },
        "SEO": {
            "function": client.get_similarweb_seo,
            "params": ["domain"]
        },
        "Website Details": {
            "function": client.get_similarweb_website_details,
            "params": ["domain"]
        }
    },
    "Instagram": {
        "User by Username": {
            "function": client.get_instagram_user_by_username,
            "params": ["username"]
        },
        "User Medias": {
            "function": client.get_instagram_user_medias,
            "params": ["user_id"]
        },
        "Media Comments": {
            "function": client.get_instagram_media_comments,
            "params": ["page_id", "can_support_threading"]
        },
        "User Followers": {
            "function": client.get_instagram_user_followers,
            "params": ["user_id"]
        },
        "Search Hashtags": {
            "function": client.search_instagram_hashtags,
            "params": ["query"]
        }
    },
    "Facebook": {
        "Page Posts": {
            "function": client.get_facebook_page_posts,
            "params": ["page_id"]
        },
        "Post Comments": {
            "function": client.get_facebook_post_comments,
            "params": ["post_id"]
        },
        "Page Reviews": {
            "function": client.get_facebook_page_reviews,
            "params": ["page_id"]
        },
        "Page Details": {
            "function": client.get_facebook_page_details,
            "params": ["url"]
        }
    },
    "Text Processing": {
        "Sentiment": {
            "function": client.process_sentiment,
            "params": ["text", "language"]
        },
        "Stem": {
            "function": client.process_stem,
            "params": ["text", "language", "stemmer"]
        },
        "Tag": {
            "function": client.process_tag,
            "params": ["text", "language", "output"]
        },
        "Phrases": {
            "function": client.process_phrases,
            "params": ["text", "language"]
        }
    }
}

def get_input_params(endpoint: Dict[str, Any]) -> Dict[str, Any]:
    """Get input parameters from user for the selected endpoint."""
    params = {}
    
    for param in endpoint["params"]:
        if param == "can_support_threading":
            params[param] = st.checkbox("Can Support Threading", value=False)
        elif param in ["language", "stemmer", "output"]:
            # For these parameters, provide dropdown options
            if param == "language":
                options = ["english", "spanish", "french", "german"]
            elif param == "stemmer":
                options = ["porter", "snowball"]
            else:  # output
                options = ["tagged", "untagged"]
            params[param] = st.selectbox(f"Select {param}", options)
        else:
            params[param] = st.text_input(f"Enter {param}")
    
    return params

# Streamlit app
st.title("RapidAPI Endpoint Tester")

# Sidebar selection
api_category = st.sidebar.selectbox("Select API Category", list(ENDPOINTS.keys()))
endpoint = st.sidebar.selectbox("Select Endpoint", list(ENDPOINTS[api_category].keys()))

# Get selected endpoint details
endpoint_details = ENDPOINTS[api_category][endpoint]

# Get input parameters
params = get_input_params(endpoint_details)

# Button to make API call
if st.button("Make API Call"):
    try:
        # Call the selected endpoint with the provided parameters
        result = endpoint_details["function"](**params)
        
        # Display result in a pretty-printed JSON format
        st.json(result, expanded=True)
    except Exception as e:
        st.error(f"Error: {str(e)}")
