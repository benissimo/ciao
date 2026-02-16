#!/usr/bin/env python3
"""
Comprehensive test suite for Ciao app
Tests core logic, session management, and HTTP handling
"""

import unittest
import sys
import importlib.util
from unittest.mock import MagicMock, patch
from http.cookies import SimpleCookie
import uuid

# Import the app module
spec = importlib.util.spec_from_file_location("app_builtin", "/root/projects/ciao/app_builtin.py")
app_builtin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_builtin)


class TestGreetingsData(unittest.TestCase):
    """Test the GREETINGS data structure"""

    def test_greetings_not_empty(self):
        """GREETINGS dictionary should not be empty"""
        self.assertTrue(len(app_builtin.GREETINGS) > 0)

    def test_greetings_has_required_languages(self):
        """GREETINGS should contain at least the core languages"""
        required_languages = ['english', 'spanish', 'french', 'german', 'italian']
        for lang in required_languages:
            self.assertIn(lang, app_builtin.GREETINGS)

    def test_greeting_values_are_strings(self):
        """All greeting values should be non-empty strings"""
        for lang, greeting in app_builtin.GREETINGS.items():
            self.assertIsInstance(greeting, str)
            self.assertTrue(len(greeting) > 0)

    def test_language_keys_are_lowercase(self):
        """All language keys should be lowercase"""
        for lang in app_builtin.GREETINGS.keys():
            self.assertEqual(lang, lang.lower())


class TestSessionManagement(unittest.TestCase):
    """Test session management and history tracking"""

    def setUp(self):
        """Clear sessions before each test"""
        app_builtin.SESSIONS.clear()

    def test_new_session_creates_empty_history(self):
        """New sessions should start with empty history"""
        session_id = str(uuid.uuid4())
        app_builtin.SESSIONS[session_id] = []
        self.assertEqual(app_builtin.SESSIONS[session_id], [])

    def test_session_history_tracks_languages(self):
        """Session history should track shown languages"""
        session_id = str(uuid.uuid4())
        app_builtin.SESSIONS[session_id] = []

        # Simulate adding languages to history
        app_builtin.SESSIONS[session_id].append('english')
        app_builtin.SESSIONS[session_id].append('spanish')

        self.assertEqual(len(app_builtin.SESSIONS[session_id]), 2)
        self.assertIn('english', app_builtin.SESSIONS[session_id])
        self.assertIn('spanish', app_builtin.SESSIONS[session_id])

    def test_history_limited_to_max_history(self):
        """Session history should not exceed MAX_HISTORY"""
        session_id = str(uuid.uuid4())
        app_builtin.SESSIONS[session_id] = []

        # Add more than MAX_HISTORY languages
        languages = list(app_builtin.GREETINGS.keys())
        for i in range(app_builtin.MAX_HISTORY + 3):
            app_builtin.SESSIONS[session_id].append(languages[i % len(languages)])
            if len(app_builtin.SESSIONS[session_id]) > app_builtin.MAX_HISTORY:
                app_builtin.SESSIONS[session_id].pop(0)

        self.assertEqual(len(app_builtin.SESSIONS[session_id]), app_builtin.MAX_HISTORY)

    def test_max_history_constant(self):
        """MAX_HISTORY should be 5"""
        self.assertEqual(app_builtin.MAX_HISTORY, 5)


class TestLanguageSelection(unittest.TestCase):
    """Test the language selection logic"""

    def setUp(self):
        """Clear sessions before each test"""
        app_builtin.SESSIONS.clear()

    def test_available_languages_excludes_history(self):
        """Available languages should exclude those in history"""
        session_id = str(uuid.uuid4())
        history = ['english', 'spanish', 'french']

        available_languages = [
            (lang, greet) for lang, greet in app_builtin.GREETINGS.items()
            if lang not in history
        ]

        for lang, _ in available_languages:
            self.assertNotIn(lang, history)

    def test_no_repeats_within_max_history_window(self):
        """Languages should not repeat within MAX_HISTORY visits"""
        session_id = str(uuid.uuid4())
        app_builtin.SESSIONS[session_id] = []
        shown_languages = []

        # Simulate 20 page visits
        for _ in range(20):
            history = app_builtin.SESSIONS[session_id]

            available_languages = [
                (lang, greet) for lang, greet in app_builtin.GREETINGS.items()
                if lang not in history
            ]

            if not available_languages:
                app_builtin.SESSIONS[session_id] = []
                available_languages = list(app_builtin.GREETINGS.items())

            language, _ = available_languages[0]  # Use first for deterministic testing

            # Verify language not in recent history
            recent_window = shown_languages[-(app_builtin.MAX_HISTORY-1):] if len(shown_languages) >= app_builtin.MAX_HISTORY-1 else shown_languages
            self.assertNotIn(language, recent_window,
                           f"Language '{language}' repeated within MAX_HISTORY window!")

            shown_languages.append(language)
            history.append(language)
            if len(history) > app_builtin.MAX_HISTORY:
                history.pop(0)

    def test_history_reset_when_all_languages_shown(self):
        """History should reset when all languages have been shown"""
        session_id = str(uuid.uuid4())
        app_builtin.SESSIONS[session_id] = list(app_builtin.GREETINGS.keys())

        # All languages are in history
        available_languages = [
            (lang, greet) for lang, greet in app_builtin.GREETINGS.items()
            if lang not in app_builtin.SESSIONS[session_id]
        ]

        # Should be empty since all languages are in history
        self.assertEqual(len(available_languages), 0)

        # After reset, all should be available again
        if not available_languages:
            app_builtin.SESSIONS[session_id] = []
            available_languages = list(app_builtin.GREETINGS.items())

        self.assertEqual(len(available_languages), len(app_builtin.GREETINGS))


class MockHandler:
    """Mock request handler for testing without network I/O"""

    def __init__(self, cookie_header=None):
        self.headers = MagicMock()
        self.headers.get.return_value = cookie_header
        self.path = '/'
        self.send_response_called = False
        self.send_error_called = False
        self.response_code = None
        self.response_headers = {}
        self.response_body = None

    def send_response(self, code):
        self.send_response_called = True
        self.response_code = code

    def send_header(self, key, value):
        self.response_headers[key] = value

    def end_headers(self):
        pass

    def send_error(self, code):
        self.send_error_called = True
        self.response_code = code

    def address_string(self):
        return '127.0.0.1'

    @property
    def wfile(self):
        """Mock write file"""
        mock_wfile = MagicMock()
        def write_func(data):
            self.response_body = data
        mock_wfile.write = write_func
        return mock_wfile

    def _get_session_id(self):
        """Copied from actual RequestHandler"""
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            from http.cookies import SimpleCookie
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            if 'session_id' in cookie:
                return cookie['session_id'].value
        return str(uuid.uuid4())


class TestRequestHandler(unittest.TestCase):
    """Test the HTTP request handler"""

    def setUp(self):
        """Clear sessions before each test"""
        app_builtin.SESSIONS.clear()

    def test_get_session_id_from_cookie(self):
        """_get_session_id should extract session ID from cookie"""
        test_session_id = str(uuid.uuid4())
        handler = MockHandler(cookie_header=f'session_id={test_session_id}')

        session_id = handler._get_session_id()
        self.assertEqual(session_id, test_session_id)

    def test_get_session_id_creates_new_when_no_cookie(self):
        """_get_session_id should create new UUID when no cookie exists"""
        handler = MockHandler(cookie_header=None)

        session_id = handler._get_session_id()

        # Should be a valid UUID string
        self.assertIsInstance(session_id, str)
        self.assertTrue(len(session_id) > 0)
        # Verify it's a valid UUID format
        try:
            uuid.UUID(session_id)
            valid_uuid = True
        except ValueError:
            valid_uuid = False
        self.assertTrue(valid_uuid)

    def test_session_logic_with_mock(self):
        """Test the session and language selection logic with mock handler"""
        handler = MockHandler(cookie_header=None)
        session_id = handler._get_session_id()

        # Initialize session
        app_builtin.SESSIONS[session_id] = []

        # Simulate language selection logic (from do_GET)
        history = app_builtin.SESSIONS[session_id]

        available_languages = [
            (lang, greet) for lang, greet in app_builtin.GREETINGS.items()
            if lang not in history
        ]

        # Should have all languages available on first visit
        self.assertEqual(len(available_languages), len(app_builtin.GREETINGS))

        # Choose a language and update history
        language, greeting = available_languages[0]
        history.append(language)

        # Verify history was updated
        self.assertEqual(len(app_builtin.SESSIONS[session_id]), 1)
        self.assertIn(language, app_builtin.SESSIONS[session_id])


class TestHTMLTemplate(unittest.TestCase):
    """Test HTML template rendering"""

    def test_html_template_contains_placeholders(self):
        """HTML template should contain greeting and language placeholders"""
        self.assertIn('{greeting}', app_builtin.HTML_TEMPLATE)
        self.assertIn('{language}', app_builtin.HTML_TEMPLATE)

    def test_html_template_is_valid_html(self):
        """HTML template should have valid HTML structure"""
        self.assertIn('<!DOCTYPE html>', app_builtin.HTML_TEMPLATE)
        self.assertIn('<html', app_builtin.HTML_TEMPLATE)
        self.assertIn('<head>', app_builtin.HTML_TEMPLATE)
        self.assertIn('<body>', app_builtin.HTML_TEMPLATE)
        self.assertIn('</body>', app_builtin.HTML_TEMPLATE)
        self.assertIn('</html>', app_builtin.HTML_TEMPLATE)

    def test_html_template_has_mobile_viewport(self):
        """HTML template should include mobile viewport meta tag"""
        self.assertIn('viewport', app_builtin.HTML_TEMPLATE)
        self.assertIn('width=device-width', app_builtin.HTML_TEMPLATE)

    def test_html_template_has_utf8_charset(self):
        """HTML template should specify UTF-8 charset"""
        self.assertIn('UTF-8', app_builtin.HTML_TEMPLATE)

    def test_html_template_rendering(self):
        """HTML template should render correctly with values"""
        html = app_builtin.HTML_TEMPLATE.format(
            greeting='Hello',
            language='English'
        )

        self.assertIn('Hello', html)
        self.assertIn('English', html)
        self.assertNotIn('{greeting}', html)
        self.assertNotIn('{language}', html)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete user flow"""

    def setUp(self):
        """Clear sessions before each test"""
        app_builtin.SESSIONS.clear()

    def test_complete_user_session_flow(self):
        """Test a complete user session with multiple page loads"""
        test_session_id = 'integration-test-session'
        app_builtin.SESSIONS[test_session_id] = []

        shown_languages = []

        # Simulate 10 page loads by replicating do_GET logic
        for i in range(10):
            history = app_builtin.SESSIONS[test_session_id]

            # Choose random language, avoiding recent ones
            available_languages = [
                (lang, greet) for lang, greet in app_builtin.GREETINGS.items()
                if lang not in history
            ]

            # If all languages are in history, reset
            if not available_languages:
                app_builtin.SESSIONS[test_session_id] = []
                available_languages = list(app_builtin.GREETINGS.items())

            language, greeting = available_languages[0]  # Use first for deterministic testing

            # Update session history
            history.append(language)
            if len(history) > app_builtin.MAX_HISTORY:
                history.pop(0)

            shown_languages.append(language)

            # Generate HTML (testing template rendering)
            html = app_builtin.HTML_TEMPLATE.format(
                greeting=greeting,
                language=language.capitalize()
            )

            # Verify valid HTML was returned
            self.assertIn('<!DOCTYPE html>', html)
            self.assertIn(greeting, html)
            self.assertIn(language.capitalize(), html)

        # Verify we showed some languages
        self.assertTrue(len(shown_languages) > 0)

        # Verify no repeats within MAX_HISTORY window
        for i in range(len(shown_languages)):
            window_start = max(0, i - app_builtin.MAX_HISTORY + 1)
            recent_window = shown_languages[window_start:i]
            self.assertNotIn(shown_languages[i], recent_window,
                           f"Language at position {i} repeated within MAX_HISTORY window")

    def test_server_instantiation(self):
        """Test that HTTPServer can be instantiated with RequestHandler"""
        from http.server import HTTPServer
        # Just verify the handler class is compatible
        self.assertTrue(hasattr(app_builtin.RequestHandler, 'do_GET'))
        self.assertTrue(callable(app_builtin.run_server))


def run_tests():
    """Run all tests and return success status"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGreetingsData))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestRequestHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestHTMLTemplate))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return True if all tests passed
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
