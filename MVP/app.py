from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "bf34651916mshccb3d44586e0275p12f940jsn401f1b484278"
API_HOST = "altapi1.p.rapidapi.com"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    company_name = request.json.get('company_name', '')
    if not company_name:
        return jsonify({"error": "Please enter a company name"}), 400

    url = f"https://altapi1.p.rapidapi.com/sentiment/amazon"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
