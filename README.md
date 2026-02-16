# Ciao - Hello in Random Languages

A simple, mobile-friendly web app that displays "Hello" in a random language each time you visit.

## Setup

### Prerequisites
- Python 3.8 or higher
- uv (recommended) or pip

### Installation

Using uv (recommended):
```bash
uv pip install -r requirements.txt
```

Using pip:
```bash
pip install -r requirements.txt
```

## Running the App

### Option 1: Flask Version (Recommended)
Requires Flask to be installed (see Installation above):
```bash
python app.py
```
The app will be available at `http://localhost:5000`

### Option 2: Built-in HTTP Server (No Dependencies)
Uses only Python's built-in http.server module:
```bash
python app_builtin.py
```
The app will be available at `http://localhost:5000`

This version is useful for environments where installing external packages is not possible.

## Development

The app randomly selects from 15 different languages each time you visit the page:
- English, Spanish, French, German, Italian
- Portuguese, Dutch, Russian, Japanese, Chinese
- Korean, Arabic, Hindi, Greek, Turkish

Each page load displays "Hello" in a different language with a clean, mobile-friendly interface.

## Tech Stack
- Python 3.8+
- Flask 3.0.0 (optional - built-in version available)
- Server-side HTML rendering
