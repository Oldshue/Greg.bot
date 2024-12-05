from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .life_coach import LifeCoachSystem

app = Flask(__name__)
CORS(app)
coach = LifeCoachSystem()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path == "":
        return send_from_directory('../public', 'index.html')
    else:
        if os.path.exists(f"../public/{path}"):
            return send_from_directory('../public', path)
        return send_from_directory('../public', 'index.html')

@app.route('/api/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        question = request.json.get('question')
        result = coach.process_user_input(question)
        return jsonify(result)  # Returns both response and notification
    except Exception as e:
        print(f"Error processing request: {str(e)}")  # Add logging
        return jsonify({'response': f"Error: {str(e)}", 'notification': None}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
