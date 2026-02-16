from flask import Flask, render_template_string
import random

app = Flask(__name__)

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

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ciao - Hello in Random Languages</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            text-align: center;
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            font-size: 4rem;
            margin: 0;
            color: #333;
        }
        p {
            font-size: 1.5rem;
            color: #666;
            margin-top: 1rem;
        }
        .reload-hint {
            margin-top: 2rem;
            font-size: 1rem;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ greeting }}</h1>
        <p>{{ language }}</p>
        <div class="reload-hint">Reload the page to see a different language</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    language, greeting = random.choice(list(GREETINGS.items()))
    return render_template_string(HTML_TEMPLATE, greeting=greeting, language=language.capitalize())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
