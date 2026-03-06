from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient


class OperationsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo')

    def setUp(self):
        self.client = APIClient()

    def test_login_and_overview(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'ops.lead', 'password': 'CommandCenter@123'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")

        overview = self.client.get('/api/overview/')
        self.assertEqual(overview.status_code, 200)
        self.assertIn('summary', overview.data)
        self.assertIn('appointments', overview.data)
