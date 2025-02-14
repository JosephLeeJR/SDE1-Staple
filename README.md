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