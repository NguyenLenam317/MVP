from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SubmitField
from rapidapi_client import RapidAPIClient
import json
from typing import Dict, Any

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

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

class APIForm(FlaskForm):
    api_category = SelectField('API Category', choices=[(cat, cat) for cat in ENDPOINTS.keys()])
    endpoint = SelectField('Endpoint', choices=[])  # Will be populated dynamically
    submit = SubmitField('Make API Call')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = APIForm()
    
    # Update endpoint choices based on selected category
    if form.api_category.data:
        form.endpoint.choices = [(ep, ep) for ep in ENDPOINTS[form.api_category.data].keys()]
    else:
        form.endpoint.choices = []
    
    result = None
    error = None
    
    if form.validate_on_submit():
        try:
            # Get selected endpoint details
            endpoint_details = ENDPOINTS[form.api_category.data][form.endpoint.data]
            
            # Get parameters from form
            params = {}
            for param in endpoint_details["params"]:
                if param == "can_support_threading":
                    params[param] = request.form.get(param, type=bool)
                elif param in ["language", "stemmer", "output"]:
                    params[param] = request.form.get(param)
                else:
                    params[param] = request.form.get(param)
            
            # Make API call
            result = endpoint_details["function"](**params)
            
        except Exception as e:
            error = str(e)
    
    return render_template('index.html', form=form, result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
