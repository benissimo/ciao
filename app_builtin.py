#!/usr/bin/env python3
"""
Ciao - Hello in Random Languages
Alternative implementation using Python's built-in http.server module
No external dependencies required
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import random
import uuid
import json
from urllib.parse import parse_qs, urlparse
from http.cookies import SimpleCookie

# Dictionary of greetings in different languages
GREETINGS = {
    'english': 'Hello',
    'spanish': 'Hola',
    'french': 'Bonjour',
    'german': 'Guten Tag',
    'italian': 'Ciao',
    'portuguese': 'Olá',
    'dutch': 'Hallo',
    'russian': 'Здравствуйте',
    'japanese': 'こんにちは',
    'chinese': '你好',
    'korean': '안녕하세요',
    'arabic': 'مرحبا',
    'hindi': 'नमस्ते',
    'greek': 'Γεια σας',
    'turkish': 'Merhaba',
}

# In-memory session storage
# sessions[session_id] = [list of recently shown languages]
SESSIONS = {}
MAX_HISTORY = 5  # Avoid repeating for at least 5 visits

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ciao - Hello in Random Languages</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            text-align: center;
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            font-size: 4rem;
            margin: 0;
            color: #333;
        }}
        p {{
            font-size: 1.5rem;
            color: #666;
            margin-top: 1rem;
        }}
        .reload-hint {{
            margin-top: 2rem;
            font-size: 1rem;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{greeting}</h1>
        <p>{language}</p>
        <div class="reload-hint">Reload the page to see a different language</div>
    </div>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            # Get or create session
            session_id = self._get_session_id()

            # Get session history
            if session_id not in SESSIONS:
                SESSIONS[session_id] = []
            history = SESSIONS[session_id]

            # Choose random language, avoiding recent ones
            available_languages = [
                (lang, greet) for lang, greet in GREETINGS.items()
                if lang not in history
            ]

            # If all languages are in history, reset history (user has seen 15+ languages)
            if not available_languages:
                SESSIONS[session_id] = []
                available_languages = list(GREETINGS.items())

            language, greeting = random.choice(available_languages)

            # Update session history
            history.append(language)
            if len(history) > MAX_HISTORY:
                history.pop(0)  # Remove oldest

            # Generate HTML
            html = HTML_TEMPLATE.format(
                greeting=greeting,
                language=language.capitalize()
            )

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; Max-Age=86400')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404)

    def _get_session_id(self):
        """Get session ID from cookie or create a new one"""
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            if 'session_id' in cookie:
                return cookie['session_id'].value

        # Create new session ID
        return str(uuid.uuid4())

    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.address_string()}] {format % args}")

def run_server(port=5000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Starting server on http://0.0.0.0:{port}')
    print('Press Ctrl+C to stop')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
