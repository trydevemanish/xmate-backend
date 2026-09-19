from pathlib import Path
from django.test import SimpleTestCase


class LoginConnectionReuseRegressionTest(SimpleTestCase):
    def test_login_view_should_not_force_a_new_db_connection(self):
        view_path = Path(__file__).resolve().parent / 'views.py'
        source = view_path.read_text(encoding='utf-8')

        self.assertNotIn('from django.db import connection', source)
        self.assertNotIn('ensure_connection()', source)
