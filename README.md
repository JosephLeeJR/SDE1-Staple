# ChatGPT Web Interface

A simple web interface for interacting with OpenAI's GPT models.

## Setup

1. Clone the repository
   ```bash
   https://github.com/<YOUR_GITHUB_USERNAME>/SDE1-Staple
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_OpenAI_api_key
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Features

- Chat interface with GPT-4o-mini
- Rate limiting to prevent abuse
- Chat history logging
- Error handling and input validation

## Routes

- `/` - Main chat interface
- `/history` - View chat history

## Testing with cURL (Windows)

You can test the API endpoints using the following cURL commands in Windows Command Prompt:

1. Test normal request:
   ```bash
   curl -X POST http://localhost:5000/openai-completion -H "Content-Type: application/json" -d "{\"prompt\": \"What is Python?\"}"
   ```

2. Test empty prompt:
   ```bash
   curl -X POST http://localhost:5000/openai-completion -H "Content-Type: application/json" -d "{\"prompt\": \"\"}"
   ```

3. Test missing prompt field:
   ```bash
   curl -X POST http://localhost:5000/openai-completion -H "Content-Type: application/json" -d "{}"
   ```

4. Test prompt length limit(Replace %a% with a string more than 1000 characters):
   ```bash
   curl -X POST http://localhost:5000/openai-completion -H "Content-Type: application/json" -d "{\"prompt\": \"%a%\"}"
   ```

5. View chat history:
   ```bash
   curl http://localhost:5000/history
   ```

Note: Make sure the application is running before executing these commands.