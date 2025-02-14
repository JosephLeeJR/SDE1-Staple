from openai import OpenAI
from flask import Flask, request, jsonify, render_template_string
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define ChatLog model
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    completion = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# Securely load API key from environment
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(api_key=api_key)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["5 per minute", "100 per hour"]
)

def validate_prompt(prompt):
    """Validate the prompt data"""
    if not isinstance(prompt, str):
        return False, "Prompt must be a string"
    if len(prompt.strip()) == 0:
        return False, "Prompt cannot be empty"
    if len(prompt) > 1000:  # 设置合理的长度限制
        return False, "Prompt too long (max 1000 characters)"
    return True, None

@app.route('/')
def home():
    html = '''
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            font-size: 18px;
        }
        .container {
            text-align: center;
            width: 80%;
            max-width: 600px;
        }
        input {
            font-size: 18px;
            padding: 10px;
            width: 70%;
            margin: 10px;
        }
        button {
            font-size: 18px;
            padding: 10px 20px;
            cursor: pointer;
        }
        #response {
            margin-top: 20px;
            font-size: 18px;
            line-height: 1.5;
        }
    </style>
    <div class="container">
        <form id="chat-form">
            <input type="text" id="prompt" placeholder="Enter your question">
            <button type="submit">Send</button>
        </form>
        <div id="response"></div>
    </div>

    <script>
    document.getElementById('chat-form').onsubmit = async (e) => {
        e.preventDefault();
        const prompt = document.getElementById('prompt').value;
        const response = await fetch('/openai-completion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt: prompt})
        });
        const data = await response.json();
        document.getElementById('response').innerText = data.response;
    };
    </script>
    '''
    return render_template_string(html)

@app.route('/openai-completion', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limit for this specific route
def get_completion():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request format',
                'message': 'Request must be valid JSON'
            }), 400

        if 'prompt' not in data:
            return jsonify({
                'error': 'Missing field',
                'message': 'Prompt field is required'
            }), 400

        # Validate prompt
        is_valid, error_message = validate_prompt(data['prompt'])
        if not is_valid:
            return jsonify({
                'error': 'Invalid prompt',
                'message': error_message
            }), 400

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": data['prompt']}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            completion_text = response.choices[0].message.content
            
            # Log the chat to database
            try:
                chat_log = ChatLog(
                    prompt=data['prompt'],
                    completion=completion_text
                )
                db.session.add(chat_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Database error: {str(db_error)}")
                # Continue returning response even if database storage fails
                
            return jsonify({'response': completion_text})

        except Exception as api_error:
            error_message = str(api_error)
            logger.error(f"OpenAI API error: {error_message}")
            
            if "Rate limit" in error_message:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Please try again later'
                }), 429
            elif "Invalid authentication" in error_message:
                return jsonify({
                    'error': 'Authentication error',
                    'message': 'API key configuration error'
                }), 401
            else:
                return jsonify({
                    'error': 'API error',
                    'message': 'Service temporarily unavailable, please try again later'
                }), 500

    except Exception as e:
        logger.error(f"General error: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'message': 'Internal server error'
        }), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests, please try again later'
    }), 429

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Server error',
        'message': 'Internal server error'
    }), 500

@app.route('/history')
def view_history():
    html = '''
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        .chat-entry {
            border: 1px solid #ddd;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        .prompt {
            margin: 10px 0;
            color: #2c5282;
        }
        .completion {
            margin: 10px 0;
            color: #2b6cb0;
        }
    </style>
    <div class="container">
        {% for chat in chats %}
        <div class="chat-entry">
            <div class="timestamp">{{ chat.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</div>
            <div class="prompt"><strong>Question:</strong> {{ chat.prompt }}</div>
            <div class="completion"><strong>Answer:</strong> {{ chat.completion }}</div>
        </div>
        {% endfor %}
    </div>
    '''
    chats = ChatLog.query.order_by(ChatLog.timestamp.desc()).all()
    return render_template_string(html, chats=chats)

if __name__ == '__main__':
    app.run(debug=True)
