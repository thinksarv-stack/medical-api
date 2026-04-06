import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from PIL import Image
import io

app = Flask(__name__)
# IMPORTANT: Allow Netlify to talk to this backend
CORS(app) 

# Initialize Gemini 3 Flash
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
You are a Medical Waste AI. Classify the image into:
1. MEDICAL_SHARP (Needles, Scalpels) - ID: 1
2. GENERAL_SHARP (Glass, Nails) - ID: 2
3. MEDICAL_WASTE (Gloves, Cotton) - ID: 3
4. GENERAL_WASTE (Paper, Plastic) - ID: 4
Output ONLY JSON: {"id": X, "category": "NAME", "reason": "why"}
"""

@app.route('/classify', methods=['POST'])
def classify():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    img = Image.open(file.stream)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[SYSTEM_PROMPT, img]
    )

    try:
        return jsonify(json.loads(response.text.strip()))
    except:
        return jsonify({"id": 4, "category": "GENERAL_WASTE", "reason": "Error parsing AI response"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
