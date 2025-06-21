from app import app
import unittest

class TestEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_main_endpoints(self):
        """Test at hovedendepunktene svarer"""
        endpoints = [
            '/',
            '/login',
            '/register',
            '/offline',  # Changed from /offline.html
            '/settings'
        ]

        for endpoint in endpoints:
            response = self.app.get(endpoint)
            self.assertIn(response.status_code, [200, 302],
                         f'Endepunkt {endpoint} svarte med status {response.status_code}')

    def test_protected_endpoints(self):
        """Test at beskyttede endepunkter krever innlogging"""
        protected_endpoints = [
            '/dashboard',
            '/notes',
            '/shared-notes',
            '/focus',  # Changed from /workboard
            '/settings'
        ]

        for endpoint in protected_endpoints:
            response = self.app.get(endpoint)
            self.assertEqual(response.status_code, 302,
                           f'Beskyttet endepunkt {endpoint} burde redirecte til login')

if __name__ == '__main__':
    unittest.main()
