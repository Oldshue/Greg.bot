from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import traceback
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .life_coach import LifeCoachSystem

app = Flask(__name__)
CORS(app)

def create_error_response(message: str, status_code: int):
    response = jsonify({
        'response': message,
        'notification': None,
        'error': True
    })
    response.status_code = status_code
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    print(f"Unhandled exception: {str(e)}")
    print(traceback.format_exc())
    # Return JSON response
    return create_error_response(
        "An internal server error occurred. Please try again later.",
        500
    )

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    try:
        if path == "":
            return send_from_directory('../public', 'index.html')
        else:
            if os.path.exists(f"../public/{path}"):
                return send_from_directory('../public', path)
            return send_from_directory('../public', 'index.html')
    except Exception as e:
        return create_error_response(str(e), 500)

@app.route('/api/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Verify request has JSON content
        if not request.is_json:
            return create_error_response("Request must be JSON", 400)

        # Get the question from JSON
        data = request.get_json()
        if not data or 'question' not in data:
            return create_error_response("No question provided", 400)

        question = data['question']

        # Initialize coach if needed
        if not hasattr(app, 'coach'):
            try:
                app.coach = LifeCoachSystem()
            except Exception as e:
                return create_error_response(
                    "Failed to initialize AI system. Please check API configuration.",
                    500
                )

        # Process the question
        try:
            result = app.coach.process_user_input(question)
            if not isinstance(result, dict):
                result = {'response': str(result), 'notification': None}
            return jsonify(result)
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            print(traceback.format_exc())
            return create_error_response(
                "Failed to process your request. Please try again.",
                500
            )

    except json.JSONDecodeError:
        return create_error_response("Invalid JSON in request", 400)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return create_error_response(
            "An unexpected error occurred. Please try again later.",
            500
        )

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
