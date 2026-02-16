#!/usr/bin/env python3
"""
Test script to verify session-based language tracking
"""

import sys
import importlib.util

# Import the app module
spec = importlib.util.spec_from_file_location("app_builtin", "/root/projects/ciao/app_builtin.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

# Mock request handler for testing
class MockHeaders:
    def __init__(self, cookie=None):
        self.cookie = cookie

    def get(self, key):
        if key == 'Cookie' and self.cookie:
            return self.cookie
        return None

class MockRequestHandler:
    def __init__(self, session_id=None):
        if session_id:
            self.headers = MockHeaders(f'session_id={session_id}')
        else:
            self.headers = MockHeaders()

    def _get_session_id(self):
        """Copied from actual handler"""
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            from http.cookies import SimpleCookie
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            if 'session_id' in cookie:
                return cookie['session_id'].value
        # For testing, return a fixed ID instead of UUID
        return "test-session-123"

def test_session_tracking():
    """Test that languages are not repeated within 5 visits"""
    print("Testing session-based language tracking...")
    print("=" * 60)

    # Create a mock handler with a fixed session ID
    handler = MockRequestHandler()
    session_id = handler._get_session_id()

    print(f"Session ID: {session_id}\n")

    # Initialize session
    app.SESSIONS[session_id] = []

    # Simulate 10 page visits
    shown_languages = []
    for i in range(10):
        # Get history
        history = app.SESSIONS[session_id]

        # Choose language (copy logic from handler)
        available_languages = [
            (lang, greet) for lang, greet in app.GREETINGS.items()
            if lang not in history
        ]

        if not available_languages:
            app.SESSIONS[session_id] = []
            available_languages = list(app.GREETINGS.items())

        language, greeting = app.random.choice(available_languages)

        # Update history
        history.append(language)
        if len(history) > app.MAX_HISTORY:
            history.pop(0)

        shown_languages.append(language)
        print(f"Visit {i+1}: {greeting} ({language})")
        print(f"  History: {history}")
        print(f"  Available: {len(available_languages)} languages")

        # Verify: current language should not be in the previous MAX_HISTORY-1 languages
        if i >= 1:
            recent = shown_languages[max(0, i-app.MAX_HISTORY+1):i]
            if language in recent:
                print(f"  ❌ ERROR: '{language}' was repeated! Last shown at position {shown_languages.index(language, max(0, i-app.MAX_HISTORY+1))}")
                return False
            else:
                print(f"  ✅ No recent repeats")
        print()

    print("=" * 60)
    print("✅ All tests passed!")
    print(f"Total languages shown: {len(shown_languages)}")
    print(f"Unique languages: {len(set(shown_languages))}")
    print(f"Languages shown: {shown_languages}")

    # Verify no repeats within sliding window of MAX_HISTORY
    for i in range(len(shown_languages)):
        window_start = max(0, i - app.MAX_HISTORY + 1)
        window = shown_languages[window_start:i]
        if shown_languages[i] in window:
            print(f"\n❌ FAIL: Language '{shown_languages[i]}' at position {i} was in recent window!")
            return False

    print("\n✅ No repeats within MAX_HISTORY window verified!")
    return True

if __name__ == '__main__':
    success = test_session_tracking()
    sys.exit(0 if success else 1)
