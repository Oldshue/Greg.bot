from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from .life_coach import LifeCoachSystem
import traceback

app = Flask(__name__)
CORS(app)

try:
    coach = LifeCoachSystem()
    print("LifeCoachSystem initialized successfully")
except Exception as e:
    print(f"Error initializing LifeCoachSystem: {str(e)}")
    traceback.print_exc()

@app.route('/api/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Debug prints
        print("Request received")
        print(f"Request JSON: {request.json}")
        
        # Check API key
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        print(f"API Key present: {bool(api_key)}")
        
        question = request.json.get('question')
        print(f"Question received: {question}")
        
        if not api_key:
            return jsonify({'response': None, 'error': 'API key not configured'}), 500
            
        response = coach.process_user_input(question)
        print(f"Response generated: {response[:100]}...")
        
        return jsonify({'response': response, 'error': None})
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in /ask endpoint: {str(e)}")
        print(f"Traceback: {error_details}")
        return jsonify({
            'response': None, 
            'error': f"Server error: {str(e)}\nDetails: {error_details}"
        }), 500

@app.route('/')
def home():
    return jsonify({"status": "API is running"})

if __name__ == '__main__':
    app.run()
