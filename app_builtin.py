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

# Dictionary of greetings in different languages with styling metadata
# Each entry includes: greeting text, primary flag color, secondary flag color, and font family
GREETINGS = {
    'english': {
        'greeting': 'Hello',
        'colors': ['#012169', '#C8102E', '#FFFFFF'],  # UK flag colors
        'font': 'Georgia, serif'
    },
    'spanish': {
        'greeting': 'Hola',
        'colors': ['#AA151B', '#F1BF00', '#AA151B'],  # Spanish flag colors
        'font': 'Georgia, serif'
    },
    'french': {
        'greeting': 'Bonjour',
        'colors': ['#0055A4', '#FFFFFF', '#EF4135'],  # French flag colors
        'font': 'Garamond, serif'
    },
    'german': {
        'greeting': 'Guten Tag',
        'colors': ['#000000', '#DD0000', '#FFCE00'],  # German flag colors
        'font': 'Arial, sans-serif'
    },
    'italian': {
        'greeting': 'Ciao',
        'colors': ['#009246', '#FFFFFF', '#CE2B37'],  # Italian flag colors
        'font': 'Palatino, serif'
    },
    'portuguese': {
        'greeting': 'Olá',
        'colors': ['#006600', '#FF0000', '#FFD700'],  # Portuguese flag colors
        'font': 'Georgia, serif'
    },
    'dutch': {
        'greeting': 'Hallo',
        'colors': ['#21468B', '#FFFFFF', '#AE1C28'],  # Dutch flag colors
        'font': 'Arial, sans-serif'
    },
    'russian': {
        'greeting': 'Здравствуйте',
        'colors': ['#FFFFFF', '#0039A6', '#D52B1E'],  # Russian flag colors
        'font': '"Times New Roman", serif'
    },
    'japanese': {
        'greeting': 'こんにちは',
        'colors': ['#FFFFFF', '#BC002D', '#FFFFFF'],  # Japanese flag colors
        'font': '"Hiragino Sans", "Noto Sans JP", sans-serif'
    },
    'chinese': {
        'greeting': '你好',
        'colors': ['#DE2910', '#FFDE00', '#DE2910'],  # Chinese flag colors
        'font': '"Microsoft YaHei", "Noto Sans SC", sans-serif'
    },
    'korean': {
        'greeting': '안녕하세요',
        'colors': ['#FFFFFF', '#CD2E3A', '#0047A0'],  # Korean flag colors
        'font': '"Malgun Gothic", "Noto Sans KR", sans-serif'
    },
    'arabic': {
        'greeting': 'مرحبا',
        'colors': ['#007A3D', '#FFFFFF', '#000000'],  # Saudi Arabia flag colors
        'font': '"Traditional Arabic", "Noto Sans Arabic", sans-serif'
    },
    'hindi': {
        'greeting': 'नमस्ते',
        'colors': ['#FF9933', '#FFFFFF', '#138808'],  # Indian flag colors
        'font': '"Noto Sans Devanagari", sans-serif'
    },
    'greek': {
        'greeting': 'Γεια σας',
        'colors': ['#0D5EAF', '#FFFFFF', '#0D5EAF'],  # Greek flag colors
        'font': '"Times New Roman", serif'
    },
    'turkish': {
        'greeting': 'Merhaba',
        'colors': ['#E30A17', '#FFFFFF', '#E30A17'],  # Turkish flag colors
        'font': 'Georgia, serif'
    },
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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: {font};
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 1rem;
            background: linear-gradient(135deg, {color1} 0%, {color2} 50%, {color3} 100%);
            transition: background 0.5s ease;
        }}
        .container {{
            text-align: center;
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 30px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.4);
            max-width: 90%;
            width: 600px;
            backdrop-filter: blur(10px);
            border: 3px solid rgba(255, 255, 255, 0.8);
        }}
        h1 {{
            font-size: clamp(2.5rem, 8vw, 5rem);
            margin: 0;
            color: {color2};
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            font-weight: 700;
            line-height: 1.2;
            word-wrap: break-word;
        }}
        p {{
            font-size: clamp(1.2rem, 4vw, 1.8rem);
            color: {color1};
            margin-top: 1.5rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        .reload-hint {{
            margin-top: 2.5rem;
            font-size: clamp(0.9rem, 2.5vw, 1.1rem);
            color: #666;
            font-style: italic;
            opacity: 0.7;
        }}
        @media (max-width: 480px) {{
            .container {{
                padding: 1.5rem;
                border-radius: 20px;
            }}
            h1 {{
                margin-bottom: 0.5rem;
            }}
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
                (lang, data) for lang, data in GREETINGS.items()
                if lang not in history
            ]

            # If all languages are in history, reset history (user has seen 15+ languages)
            if not available_languages:
                SESSIONS[session_id] = []
                available_languages = list(GREETINGS.items())

            language, lang_data = random.choice(available_languages)

            # Update session history
            history.append(language)
            if len(history) > MAX_HISTORY:
                history.pop(0)  # Remove oldest

            # Generate HTML with dynamic styling
            html = HTML_TEMPLATE.format(
                greeting=lang_data['greeting'],
                language=language.capitalize(),
                color1=lang_data['colors'][0],
                color2=lang_data['colors'][1],
                color3=lang_data['colors'][2],
                font=lang_data['font']
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
